"""Request and response schemas for the API Gateway service."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PingResponse(BaseModel):
    """Response schema for the healthcheck ping endpoint."""

    status: str = Field(default="ok", description="Status of the API gateway")
    environment: str = Field(..., description="Active deployment environment")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Server current UTC time"
    )
    version: str = Field(default="0.1.0", description="Service version")


class ErrorDetail(BaseModel):
    """Schema representing detailed information about an error."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, List[str]]] = Field(
        default=None, description="Detailed field-level validation errors or metadata"
    )


class HTTPErrorResponse(BaseModel):
    """Generic schema for returned HTTP errors."""

    error: ErrorDetail = Field(..., description="Details of the occurred error")


# --- Authentication Schemas ---


class LoginRequest(BaseModel):
    """Schema for user credentials authentication request."""

    username: str = Field(..., description="Registered username")
    password: str = Field(..., description="Plaintext password")


class LoginResponse(BaseModel):
    """Schema for access and refresh tokens returned on successful login."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type prefix")


class RefreshRequest(BaseModel):
    """Schema for refreshing access tokens."""

    refresh_token: str = Field(..., description="Valid JWT refresh token")


class RefreshResponse(BaseModel):
    """Schema for access token returned after validation of refresh token."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type prefix")


# --- Admin User Schemas ---


class UserCreate(BaseModel):
    """Schema for creating a user by administrator."""

    username: str = Field(..., description="Target username")
    password: str = Field(..., description="Clear text initial password")
    role: str = Field(default="user", description="Assigned role ('admin' or 'user')")


class UserResponse(BaseModel):
    """Response schema representing a user record."""

    id: str = Field(..., description="Format: usr_xxx")
    username: str = Field(..., description="Unique username")
    role: str = Field(..., description="Role of the user")
    is_active: bool = Field(..., description="Account active flag")
    created_at: datetime = Field(..., description="Creation date and time")


# --- Verification Plan Schema (Legacy but useful) ---


class VerificationPlanSchema(BaseModel):
    """Schema for the validation/verification plan of a hypothesis."""

    experiments: List[str] = Field(
        ..., description="List of experiments required to verify the hypothesis"
    )
    resources: List[str] = Field(
        ..., description="Equipment, materials, or software required"
    )
    success_criteria: str = Field(
        ..., description="Quantitative or qualitative criteria for success"
    )


# --- Hypothesis Schema (Legacy/Direct) ---


class HypothesisCreate(BaseModel):
    """Schema for creating or generating a new scientific hypothesis directly."""

    problem_statement: str = Field(
        ...,
        description="The target problem to solve, e.g., 'снизить потери никеля в хвостах флотации'",
    )
    constraints: Optional[List[str]] = Field(
        default=None,
        description="List of constraints, e.g., equipment limits, budget, env regulations",
    )
    knowledge_base_ids: Optional[List[str]] = Field(
        default=None,
        description="References to source documents/patents to use for justification",
    )


class HypothesisResponse(BaseModel):
    """Schema for a fully formed and ranked scientific hypothesis."""

    id: str = Field(..., description="Unique hypothesis identifier")
    formulation: str = Field(
        ...,
        description="Concrete formulation including reagents, dosages, and expected outcome",
    )
    scientific_basis: str = Field(
        ..., description="Scientific justification with citations from the sources"
    )
    expected_mechanism: str = Field(
        ..., description="Physical/chemical mechanism of the impact"
    )
    novelty: int = Field(
        ..., ge=1, le=5, description="Novelty rating of the hypothesis (1-5)"
    )
    risks: Dict[str, str] = Field(
        ...,
        description="Identified risks categorized by type (technical, economic, ecological)",
    )
    expected_value: str = Field(
        ..., description="Expected impact on Key Performance Indicators (KPI)"
    )
    verification_plan: VerificationPlanSchema = Field(
        ..., description="Detailed verification path"
    )
    score: float = Field(
        ..., description="Aggregated rank score for ordering hypotheses"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Time of generation"
    )


# --- Message Schemas ---


class MessageResponse(BaseModel):
    """Schema for representing conversation message details."""

    id: str = Field(..., description="Format: msg_xxx")
    role: str = Field(..., description="Sender role ('user' or 'system')")
    content: str = Field(..., description="Text content of the message")
    iteration: int = Field(..., description="Iteration number in the session")
    status: str = Field(
        ...,
        description="Status of processing ('queued', 'processing', 'done', 'failed')",
    )
    task_id: Optional[str] = Field(
        default=None, description="Celery task ID if applicable"
    )
    created_at: datetime = Field(..., description="Creation date and time")


class MessageListResponse(BaseModel):
    """Schema for paginated message list."""

    items: List[MessageResponse] = Field(..., description="List of messages")
    total: int = Field(..., description="Total count of messages in session")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size limit")


class MessageCreateResponse(BaseModel):
    """Response returned upon submission of a new message/task."""

    message_id: str = Field(..., description="Format: msg_xxx")
    task_id: str = Field(..., description="Celery Task ID")
    status: str = Field(..., description="Initial processing status")


# --- Pipeline Output & Result Schemas ---


class HypothesisCard(BaseModel):
    """Detailed scientific hypothesis details returned from pipeline."""

    title: str = Field(..., description="Hypothesis title")
    problem: str = Field(..., description="Prompt problem statement")
    hypothesis: str = Field(..., description="Full hypothesis formulation")
    expected_effect: str = Field(..., description="Expected effect on KPI")
    risks: List[str] = Field(..., description="Identified technical/economic risks")
    feasibility_score: float = Field(..., description="Feasibility score (0-10)")
    novelty_score: float = Field(..., description="Novelty score (0-10)")
    effect_score: float = Field(..., description="Effectiveness score (0-10)")
    risk_score: float = Field(..., description="Risk score (0-10)")
    evidence_sources: List[str] = Field(
        ..., description="Citations and evidence documents"
    )
    supporting_nodes: List[str] = Field(..., description="Entities referenced in graph")
    source_chunks: List[str] = Field(
        ..., description="Source text chunk identifiers used"
    )


class HypothesisReview(BaseModel):
    """Expert evaluation scores and notes from pipeline."""

    hypothesis_id: str = Field(..., description="Target hypothesis identifier")
    scores: Dict[str, float] = Field(..., description="Component review scores")
    comments: Dict[str, str] = Field(..., description="Specific comments per score")
    verdict: str = Field(..., description="Final verdict, e.g. 'accept'")
    suggestions: List[str] = Field(..., description="Improvements suggestions")


class GraphNode(BaseModel):
    """Knowledge graph entity node."""

    id: str = Field(..., description="Node unique ID")
    label: str = Field(..., description="Type: Material, Process, Property...")
    name: str = Field(..., description="Normalized entity name")
    source_chunks: List[str] = Field(default_factory=list, description="Source chunks")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata dictionary"
    )


class GraphEdge(BaseModel):
    """Knowledge graph relationship edge."""

    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relation: str = Field(..., description="Relation type (e.g. influences)")
    confidence: float = Field(default=1.0, description="Confidence level (0.0-1.0)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata dictionary"
    )


class GraphChain(BaseModel):
    """Logical reasoning chain within graph."""

    chain_id: str = Field(..., description="Reasoning chain ID")
    node_ids: List[str] = Field(..., description="Sequence of node IDs in chain")
    edge_labels: List[str] = Field(..., description="Sequence of edge relations")
    summary: str = Field(..., description="Human readable summary of reasoning chain")


class GraphResponse(BaseModel):
    """Complete Knowledge Graph representation."""

    nodes: List[GraphNode] = Field(..., description="Entities in the graph")
    edges: List[GraphEdge] = Field(..., description="Relationships in the graph")
    chains: List[GraphChain] = Field(
        default_factory=list, description="Extracted reasoning paths"
    )


class TraceResult(BaseModel):
    """Trace metadata of pipeline execution."""

    session_id: str = Field(..., description="Session identifier")
    iteration: int = Field(..., description="Iteration index")
    chunks_used: List[str] = Field(..., description="List of source text chunks")
    tables_queried: List[str] = Field(..., description="Referenced database tables")
    history_cases_used: List[str] = Field(..., description="Relevant historical cases")


class ResultResponse(BaseModel):
    """Response representing results of processing a message."""

    message_id: str = Field(..., description="Associated system message ID")
    status: str = Field(..., description="Processing status")
    hypothesis: Optional[HypothesisCard] = Field(
        default=None, description="Generated hypothesis card if successful"
    )
    review: Optional[HypothesisReview] = Field(
        default=None, description="Expert review if successful"
    )
    graph: Optional[GraphResponse] = Field(
        default=None, description="Extracted knowledge graph if successful"
    )
    trace: Optional[TraceResult] = Field(
        default=None, description="Execution trace if successful"
    )
    task_id: Optional[str] = Field(
        default=None, description="Downstream task ID if processing"
    )


# --- Session Schemas ---


class SessionCreate(BaseModel):
    """Schema for initializing a new research session."""

    title: str = Field(..., description="Title of the research topic")
    constraints: Optional[str] = Field(
        default=None, description="Text describing budget or equipment constraints"
    )
    weights: Optional[Dict[str, float]] = Field(
        default=None, description="Custom weights for criteria evaluation"
    )


class SessionResponse(BaseModel):
    """Basic response details representing a session."""

    id: str = Field(..., description="Format: sess_xxx")
    title: str = Field(..., description="Session title")
    status: str = Field(..., description="Status (created, processing, done, failed)")
    created_at: datetime = Field(..., description="Creation date and time")
    updated_at: datetime = Field(..., description="Last update date and time")


class SessionListResponse(BaseModel):
    """Schema for paginated session query response."""

    items: List[SessionResponse] = Field(..., description="List of sessions")
    total: int = Field(..., description="Total count of sessions for current user")


class SessionDetailResponse(BaseModel):
    """Detailed response representation of a session including history and last result."""

    id: str = Field(..., description="Format: sess_xxx")
    title: str = Field(..., description="Session title")
    constraints: Optional[str] = Field(
        default=None, description="Session constraints string"
    )
    weights: Optional[Dict[str, float]] = Field(
        default=None, description="Evaluation criterion weights"
    )
    status: str = Field(..., description="Current session status")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")
    messages: List[MessageResponse] = Field(
        default_factory=list, description="Message log associated with session"
    )
    latest_result: Optional[ResultResponse] = Field(
        default=None, description="Most recent pipeline results if available"
    )


# --- Tasks Schemas ---


class TaskStatusResponse(BaseModel):
    """Celery task status representation."""

    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Current task status")
    result: Optional[Any] = Field(default=None, description="Task output result")
