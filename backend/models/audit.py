from typing import Literal

from pydantic import BaseModel, Field


class ClaimAudit(BaseModel):
    """
    Verification result for one claim from the generated pitch.
    """

    claim: str

    claim_type: str

    status: Literal[
        "supported",
        "unsupported",
        "partially_supported",
    ]

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    explanation: str

    source_document: str | None = None

    source_page: int | None = Field(
        default=None,
        ge=1,
    )

    source_chunk_id: str | None = None

    evidence: str | None = None


class AuditReport(BaseModel):
    """
    Complete audit report for a generated pitch.
    """

    company_name: str

    policy_provider: str

    policy_product: str | None = None

    claims: list[ClaimAudit] = Field(
        default_factory=list
    )

    total_claims: int = Field(
        ge=0
    )

    supported_claims: int = Field(
        ge=0
    )

    partially_supported_claims: int = Field(
        ge=0
    )

    unsupported_claims: int = Field(
        ge=0
    )

    audit_passed: bool