from __future__ import annotations

from ner import extract_document, extract_entities

from ai_pipeline.agents.generator import GeneratorAgent
from ai_pipeline.agents.graph_agent import GraphAgent
from ai_pipeline.agents.relation_extractor import RelationExtractor
from ai_pipeline.agents.reviewer import ReviewerAgent
from ai_pipeline.chunking.hybrid_chunker import HybridChunker
from ai_pipeline.embeddings.yandex_embedder import YandexEmbedder
from ai_pipeline.rag.history_rag import HistoryRAG
from ai_pipeline.rag.knowledge_rag import KnowledgeRAG
from ai_pipeline.rag.relation_rag import RelationRAG
from ai_pipeline.state import (
    PipelineInput,
    PipelineOutput,
    PipelineState,
    PipelineTrace,
    RevisionRecord,
)
from ai_pipeline.tools.postgres_tools import PostgresTools


class HypothesisPipeline:
    def __init__(self) -> None:
        self.chunker = HybridChunker()
        self.embedder = YandexEmbedder()
        self.knowledge_rag = KnowledgeRAG()
        self.history_rag = HistoryRAG()
        self.relation_rag = RelationRAG()
        self.generator = GeneratorAgent()
        self.reviewer = ReviewerAgent()
        self.relation_extractor = RelationExtractor()
        self.graph_agent = GraphAgent()
        self.postgres_tools = PostgresTools()

    async def run(self, input_data: PipelineInput) -> PipelineOutput:
        state = PipelineState(
            input=input_data,
            trace=PipelineTrace(
                session_id=input_data.session_id or "",
                iteration=input_data.iteration,
            ),
        )

        if (
            input_data.iteration > 0
            and not input_data.new_documents
            and input_data.document is None
            and input_data.file_path is None
        ):
            state.requires_chunking = False
        else:
            state.requires_chunking = True

        if input_data.iteration > 0 and input_data.feedback:
            pass

        state = await self._run(state)
        return state.output

    async def _run(self, state: PipelineState) -> PipelineState:
        state = await self._ingest_document(state)
        state = await self._extract_entities_ner(state)
        state = await self._extract_relations(state)
        state = await self._chunk_and_embed(state)
        state = await self._index_relations(state)
        state = await self._retrieve_knowledge(state)
        state = await self._retrieve_history(state)
        state = await self._generate_hypothesis(state)
        state = self._build_graph(state)
        state = await self._review_hypothesis(state)
        state = self._build_output(state)
        await self._store_history(state)
        return state

    async def _chunk_and_embed(self, state: PipelineState) -> PipelineState:
        if not state.requires_chunking:
            return state

        document = state.input.document
        if not document:
            return state

        chunks = self.chunker.chunk(document)
        chunks = self.embedder.embed(chunks)
        state.chunks = chunks

        from ai_pipeline.vector_store.chroma_store import ChromaStore

        store = ChromaStore()
        store.populate_knowledge(chunks)

        return state

    async def _retrieve_knowledge(self, state: PipelineState) -> PipelineState:
        problem = state.input.problem
        if not problem:
            return state

        chunks, context = self.knowledge_rag.retrieve(problem)
        state.trace.chunks_used = [c.chunk_id for c in chunks][:20]

        _, rel_context = self.relation_rag.retrieve(problem)
        if rel_context:
            context += "\n\n--- Связи между сущностями ---\n" + rel_context

        state.rag_context = context

        if not state.chunks and not state.requires_chunking:
            state.chunks = chunks

        return state

    async def _retrieve_history(self, state: PipelineState) -> PipelineState:
        problem = state.input.problem
        if not problem:
            return state

        context = self.history_rag.retrieve_similar(
            problem,
            user_id=state.input.user_id,
        )
        state.history_context = context

        return state

    async def _ingest_document(self, state: PipelineState) -> PipelineState:
        if state.document is not None:
            return state
        fp = state.input.file_path
        if not fp:
            return state
        state.document = extract_document(fp)
        return state

    async def _extract_entities_ner(
        self, state: PipelineState
    ) -> PipelineState:
        document = state.document or state.input.document
        if not document:
            return state
        entities = extract_entities(document)
        state.ner_entities = entities
        state.entities = entities
        return state

    async def _extract_relations(self, state: PipelineState) -> PipelineState:
        if not state.ner_entities:
            return state
        document = state.document or state.input.document
        if not document:
            return state
        doc_text = " ".join(el.embedding_payload for el in document.elements)
        relations = await self.relation_extractor.extract(
            entities=state.ner_entities,
            document_text=doc_text,
        )
        state.relations = relations
        return state

    async def _index_relations(self, state: PipelineState) -> PipelineState:
        if not state.relations:
            return state
        doc_id = ""
        if state.document:
            doc_id = state.document.document_id
        elif state.input.document:
            doc_id = state.input.document.document_id
        self.relation_rag.index_relations(
            relations=state.relations,
            entities=state.ner_entities,
            document_id=doc_id,
        )
        return state

    async def _generate_hypothesis(
        self, state: PipelineState
    ) -> PipelineState:
        hypothesis = await self.generator.generate(
            problem=state.input.problem,
            constraints=state.input.constraints,
            weights=state.input.weights,
            rag_context=state.rag_context,
            history_context=state.history_context,
            feedback=state.input.feedback,
            chunks=state.chunks,
        )

        for chunk_id in hypothesis.source_chunks:
            if chunk_id not in state.trace.chunks_used:
                state.trace.chunks_used.append(chunk_id)

        state.hypothesis = hypothesis

        if state.input.iteration > 0:
            state.trace.revision_history.append(
                RevisionRecord(
                    iteration=state.input.iteration,
                    hypothesis=hypothesis,
                    feedback=state.input.feedback,
                )
            )

        return state

    def _build_graph(self, state: PipelineState) -> PipelineState:
        entities = state.ner_entities or state.entities
        if not entities:
            return state

        doc_id = ""
        if state.document:
            doc_id = state.document.document_id
        elif state.input.document:
            doc_id = state.input.document.document_id

        relations = self.relation_rag.retrieve_by_document(doc_id)

        graph = self.graph_agent.build(
            entities=entities,
            relations=relations,
        )
        state.graph = graph

        self.relation_rag.index_chains(graph.chains, doc_id)

        return state

    async def _review_hypothesis(self, state: PipelineState) -> PipelineState:
        hypothesis = state.hypothesis
        if not hypothesis:
            return state

        review = await self.reviewer.review(hypothesis)
        state.review = review

        return state

    def _build_output(self, state: PipelineState) -> PipelineState:
        state.output = PipelineOutput(
            hypothesis=state.hypothesis,
            review=state.review,
            graph=state.graph,
            trace=state.trace,
        )

        return state

    async def _store_history(self, state: PipelineState) -> PipelineState:
        if not state.hypothesis or not state.review:
            return state

        self.history_rag.store_result(
            hypothesis=state.hypothesis,
            review=state.review,
            user_feedback=state.input.feedback,
            user_id=state.input.user_id,
        )

        return state
