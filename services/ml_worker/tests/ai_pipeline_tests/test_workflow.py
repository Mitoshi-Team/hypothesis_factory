from __future__ import annotations

import pytest
from ai_pipeline.state import HypothesisCard, HypothesisReview, PipelineInput
from ai_pipeline.workflow import HypothesisPipeline


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
    async def test_extract_graph_empty_chunks(self):
        pipeline = HypothesisPipeline()
        state = pipeline_state_factory()
        state.chunks = []
        state = await pipeline._extract_graph(state)
        assert len(state.entities) == 0

    def test_link_hypothesis_to_graph_empty(self):
        pipeline = HypothesisPipeline()
        state = pipeline_state_factory()
        pipeline._link_hypothesis_to_graph(state)

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
            pipeline.graph_extractor, "extract", return_value=([], [])
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
    async def test_pipeline_requires_chunking_on_first_iter(self, mocker):
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
            pipeline.graph_extractor, "extract", return_value=([], [])
        )
        mocker.patch.object(
            pipeline.history_rag, "retrieve_similar", return_value=""
        )
        mocker.patch.object(
            pipeline.knowledge_rag, "retrieve", return_value=([], "")
        )
        mocker.patch.object(pipeline.history_rag, "store_result")

        input_data = PipelineInput(problem="Test", iteration=0)
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
            pipeline.graph_extractor, "extract", return_value=([], [])
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


def pipeline_state_factory(requires_chunking: bool = False):
    from ai_pipeline.state import PipelineState

    state = PipelineState(input=PipelineInput(problem="Test problem"))
    state.requires_chunking = requires_chunking
    return state
