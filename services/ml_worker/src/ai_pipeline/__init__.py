from __future__ import annotations

from ai_pipeline.state import PipelineInput, PipelineOutput
from ai_pipeline.workflow import HypothesisPipeline


async def run_pipeline(input_data: PipelineInput) -> PipelineOutput:
    pipeline = HypothesisPipeline()
    return await pipeline.run(input_data)


__all__ = [
    "run_pipeline",
    "PipelineInput",
    "PipelineOutput",
    "HypothesisPipeline",
]
