"""Request and response schemas for the API Gateway service."""

from datetime import datetime
from typing import Dict, List, Optional

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


class HypothesisCreate(BaseModel):
    """Schema for creating or generating a new scientific hypothesis."""

    problem_statement: str = Field(
        ...,
        description=(
            "The target problem to solve, e.g., "
            "'снизить потери никеля в хвостах флотации'"
        ),
    )
    constraints: Optional[List[str]] = Field(
        default=None,
        description=(
            "List of constraints, e.g., equipment limits, budget, env regulations"
        ),
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
        description=(
            "Concrete formulation including reagents, dosages, and expected outcome"
        ),
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
        description=(
            "Identified risks categorized by type (technical, economic, ecological)"
        ),
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
