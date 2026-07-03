from __future__ import annotations

from ai_pipeline.agents.generator import GeneratorAgent
from ai_pipeline.agents.graph_extractor import GraphExtractorAgent
from ai_pipeline.agents.reviewer import ReviewerAgent
from ai_pipeline.chunking.hybrid_chunker import HybridChunker
from ai_pipeline.embeddings.yandex_embedder import YandexEmbedder
from ai_pipeline.graph.builder import GraphBuilder
from ai_pipeline.rag.history_rag import HistoryRAG
from ai_pipeline.rag.knowledge_rag import KnowledgeRAG
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
        self.generator = GeneratorAgent()
        self.reviewer = ReviewerAgent()
        self.graph_extractor = GraphExtractorAgent()
        self.graph_builder = GraphBuilder()
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
        ):
            state.requires_chunking = False
        else:
            state.requires_chunking = True

        if input_data.iteration > 0 and input_data.feedback:
            pass

        state = await self._run(state)
        return state.output

    async def _run(self, state: PipelineState) -> PipelineState:
        state = await self._chunk_and_embed(state)
        state = await self._retrieve_knowledge(state)
        state = await self._retrieve_history(state)
        state = await self._extract_graph(state)
        state = await self._generate_hypothesis(state)
        state = self._link_hypothesis_to_graph(state)
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
        state.rag_context = context
        state.trace.chunks_used = [c.chunk_id for c in chunks][:20]

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

    async def _extract_graph(self, state: PipelineState) -> PipelineState:
        chunks = state.chunks
        if not chunks:
            return state

        entities, relations = await self.graph_extractor.extract(chunks[:5])
        state.entities = entities
        state.relations = relations

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

    def _link_hypothesis_to_graph(self, state: PipelineState) -> PipelineState:
        hypothesis = state.hypothesis
        entities = state.entities

        if not hypothesis or not entities:
            return state

        hypothesis.supporting_nodes = [e.entity_id for e in entities[:5]]
        return state

    async def _review_hypothesis(self, state: PipelineState) -> PipelineState:
        hypothesis = state.hypothesis
        if not hypothesis:
            return state

        review = await self.reviewer.review(hypothesis)
        state.review = review

        return state

    def _build_output(self, state: PipelineState) -> PipelineState:
        graph = self.graph_builder.build(
            entities=state.entities,
            relations=state.relations,
            hypothesis=state.hypothesis,
        )
        state.graph = graph

        state.output = PipelineOutput(
            hypothesis=state.hypothesis,
            review=state.review,
            graph=graph,
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
