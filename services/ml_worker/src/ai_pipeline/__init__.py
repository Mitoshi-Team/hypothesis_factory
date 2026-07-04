from __future__ import annotations

from src.ai_pipeline.state import PipelineInput, PipelineOutput
from src.ai_pipeline.workflow import HypothesisPipeline


async def run_pipeline(input_data: PipelineInput) -> PipelineOutput:
    pipeline = HypothesisPipeline(session_id=input_data.session_id or "")
    return await pipeline.run(input_data)


__all__ = [
    "run_pipeline",
    "PipelineInput",
    "PipelineOutput",
    "HypothesisPipeline",
]
