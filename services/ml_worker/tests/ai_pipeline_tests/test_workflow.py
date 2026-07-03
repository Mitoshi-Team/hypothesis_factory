from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from src.ai_pipeline.state import (
    HypothesisCard,
    HypothesisReview,
    PipelineInput,
)
from src.ai_pipeline.workflow import HypothesisPipeline


class TestHypothesisPipeline:
    @pytest.mark.asyncio
    async def test_chunk_and_embed_skipped_when_no_document(self):
        pipeline = HypothesisPipeline()
        state = pipeline_state_factory(requires_chunking=True)
        state = await pipeline._chunk_and_embed(state)
        assert state.chunks == []

    @pytest.mark.asyncio
    async def test_retrieve_knowledge_empty_problem(self):
        pipeline = HypothesisPipeline()
        state = pipeline_state_factory()
        state.input.problem = ""
        state = await pipeline._retrieve_knowledge(state)
        assert state.rag_context == ""

    @pytest.mark.asyncio
    async def test_retrieve_history_empty_problem(self):
        pipeline = HypothesisPipeline()
        state = pipeline_state_factory()
        state.input.problem = ""
        state = await pipeline._retrieve_history(state)
        assert state.history_context == ""

    @pytest.mark.asyncio
    async def test_ingest_document_no_file_path(self):
        pipeline = HypothesisPipeline()
        state = pipeline_state_factory()
        state = await pipeline._ingest_document(state)
        assert state.document is None

    @pytest.mark.asyncio
    async def test_extract_entities_ner_no_document(self):
        pipeline = HypothesisPipeline()
        state = pipeline_state_factory()
        state = await pipeline._extract_entities_ner(state)
        assert state.ner_entities == []

    @pytest.mark.asyncio
    async def test_extract_relations_no_entities(self):
        pipeline = HypothesisPipeline()
        state = pipeline_state_factory()
        state = await pipeline._extract_relations(state)
        assert state.relations == []

    def test_build_graph_no_entities(self):
        pipeline = HypothesisPipeline()
        state = pipeline_state_factory()
        pipeline._build_graph(state)

    def test_build_output(self):
        pipeline = HypothesisPipeline()
        state = pipeline_state_factory()
        state.hypothesis = None
        state = pipeline._build_output(state)
        assert state.output is not None

    @pytest.mark.asyncio
    async def test_full_pipeline_with_minimal_input(self, mocker):
        pipeline = HypothesisPipeline()
        fake_hypothesis = HypothesisCard(
            title="Test", problem="Test", hypothesis="Some hypothesis"
        )
        fake_review = HypothesisReview(
            scores={"novelty": 8, "feasibility": 7, "effect": 9, "risk": 3},
            verdict="accept",
            comments={"general": "Good work"},
        )
        mocker.patch.object(
            pipeline.generator, "generate", return_value=fake_hypothesis
        )
        mocker.patch.object(
            pipeline.reviewer, "review", return_value=fake_review
        )
        mocker.patch.object(
            pipeline.relation_extractor, "extract", return_value=[]
        )
        mocker.patch.object(pipeline.relation_rag, "index_relations")
        mocker.patch.object(
            pipeline.relation_rag, "retrieve", return_value=([], "")
        )
        mocker.patch.object(
            pipeline.history_rag, "retrieve_similar", return_value=""
        )
        mocker.patch.object(
            pipeline.knowledge_rag, "retrieve", return_value=([], "")
        )
        mocker.patch.object(pipeline.history_rag, "store_result")

        input_data = PipelineInput(problem="Test problem")
        output = await pipeline.run(input_data)
        assert output is not None

    @pytest.mark.asyncio
    async def test_pipeline_with_file_path_skips_chunking(self, mocker):
        pipeline = HypothesisPipeline()
        fake_doc = MagicMock()
        fake_doc.elements = []
        fake_doc.document_id = "doc_test"

        mocker.patch(
            "src.ai_pipeline.workflow.extract_document", return_value=fake_doc
        )
        mocker.patch(
            "src.ai_pipeline.workflow.extract_entities", return_value=[]
        )
        mocker.patch.object(
            pipeline.relation_extractor, "extract", return_value=[]
        )
        mocker.patch.object(pipeline.relation_rag, "index_relations")
        mocker.patch.object(
            pipeline.relation_rag, "retrieve", return_value=([], "")
        )
        mocker.patch.object(
            pipeline.knowledge_rag, "retrieve", return_value=([], "")
        )
        mocker.patch.object(
            pipeline.history_rag, "retrieve_similar", return_value=""
        )
        mocker.patch.object(pipeline.history_rag, "store_result")
        mocker.patch.object(
            pipeline.generator,
            "generate",
            return_value=HypothesisCard(
                title="T", problem="P", hypothesis="H"
            ),
        )
        mocker.patch.object(
            pipeline.reviewer,
            "review",
            return_value=HypothesisReview(verdict="accept"),
        )

        input_data = PipelineInput(problem="Test", file_path="/fake/path.pdf")
        output = await pipeline.run(input_data)
        assert output is not None

    @pytest.mark.asyncio
    async def test_pipeline_skips_chunking_on_feedback_only(self, mocker):
        pipeline = HypothesisPipeline()
        fake_hypothesis = HypothesisCard(
            title="Test", problem="Test", hypothesis="Some hypothesis"
        )
        fake_review = HypothesisReview(
            scores={"novelty": 8, "feasibility": 7, "effect": 9, "risk": 3},
            verdict="accept",
            comments={"general": "Good work"},
        )
        mocker.patch.object(
            pipeline.generator, "generate", return_value=fake_hypothesis
        )
        mocker.patch.object(
            pipeline.reviewer, "review", return_value=fake_review
        )
        mocker.patch.object(
            pipeline.relation_extractor, "extract", return_value=[]
        )
        mocker.patch.object(pipeline.relation_rag, "index_relations")
        mocker.patch.object(
            pipeline.relation_rag, "retrieve", return_value=([], "")
        )
        mocker.patch.object(
            pipeline.history_rag, "retrieve_similar", return_value=""
        )
        mocker.patch.object(
            pipeline.knowledge_rag, "retrieve", return_value=([], "")
        )
        mocker.patch.object(pipeline.history_rag, "store_result")

        input_data = PipelineInput(
            problem="Test", iteration=2, feedback="Make it better"
        )
        output = await pipeline.run(input_data)
        assert output is not None

    @pytest.mark.asyncio
    async def test_retrieve_knowledge_includes_relations(self, mocker):
        pipeline = HypothesisPipeline()
        mocker.patch.object(
            pipeline.knowledge_rag,
            "retrieve",
            return_value=(
                [MagicMock(chunk_id="c1")],
                "Some chunk context",
            ),
        )
        mocker.patch.object(
            pipeline.relation_rag,
            "retrieve",
            return_value=(
                [],
                "Nickel [influences] Strength",
            ),
        )

        state = pipeline_state_factory()
        state.input.problem = "nickel strength"
        state = await pipeline._retrieve_knowledge(state)
        assert "Nickel" in state.rag_context
        assert "influences" in state.rag_context
        assert "chunk" in state.rag_context


def pipeline_state_factory(requires_chunking: bool = False):
    from src.ai_pipeline.state import PipelineState

    state = PipelineState(input=PipelineInput(problem="Test problem"))
    state.requires_chunking = requires_chunking
    return state
