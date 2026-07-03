from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from models import (
    Chunk,
    Entity,
    Relation,
    UnifiedDocument,
)
from pydantic import BaseModel

from ai_pipeline.graph.graph_schema import KnowledgeGraph


class HypothesisCard(BaseModel):
    title: str = ""
    problem: str = ""
    hypothesis: str = ""
    expected_effect: str = ""
    risks: list[str] = []
    feasibility_score: float = 0.0
    novelty_score: float = 0.0
    effect_score: float = 0.0
    risk_score: float = 0.0
    evidence_sources: list[str] = []
    supporting_nodes: list[str] = []
    source_chunks: list[str] = []


class HypothesisReview(BaseModel):
    hypothesis_id: str = ""
    scores: dict[str, float] = {}
    comments: dict[str, str] = {}
    verdict: str = "revise"
    suggestions: list[str] = []


class RevisionRecord(BaseModel):
    iteration: int = 0
    hypothesis: HypothesisCard = HypothesisCard()
    feedback: Optional[str] = None
    verdict: str = "revise"


class HistoryEntry(BaseModel):
    entry_id: str = ""
    user_id: str = ""
    problem: str = ""
    hypothesis_text: str = ""
    verdict: str = ""
    scores: dict[str, float] = {}
    review_comment: str = ""
    user_feedback: Optional[str] = None
    is_positive_example: bool = False
    timestamp: str = ""


class PipelineTrace(BaseModel):
    session_id: str = ""
    iteration: int = 0
    chunks_used: list[str] = []
    tables_queried: list[str] = []
    history_cases_used: list[str] = []
    revision_history: list[RevisionRecord] = []


class PipelineInput(BaseModel):
    session_id: Optional[str] = None
    user_id: str = ""
    problem: str = ""
    file_path: Optional[str] = None
    document: Optional[UnifiedDocument] = None
    constraints: str = ""
    weights: Optional[dict[str, float]] = None
    iteration: int = 0
    feedback: Optional[str] = None
    new_documents: list[UnifiedDocument] = []


class PipelineOutput(BaseModel):
    hypothesis: Optional[HypothesisCard] = None
    review: Optional[HypothesisReview] = None
    graph: Optional[KnowledgeGraph] = None
    trace: Optional[PipelineTrace] = None


@dataclass
class PipelineState:
    input: PipelineInput = field(default_factory=PipelineInput)
    output: PipelineOutput = field(default_factory=PipelineOutput)

    document: Optional[UnifiedDocument] = None
    chunks: list[Chunk] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    ner_entities: list[Entity] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)

    rag_context: str = ""
    history_context: str = ""
    graph: Optional[KnowledgeGraph] = None
    hypothesis: Optional[HypothesisCard] = None
    review: Optional[HypothesisReview] = None
    trace: PipelineTrace = field(default_factory=PipelineTrace)

    requires_chunking: bool = True
