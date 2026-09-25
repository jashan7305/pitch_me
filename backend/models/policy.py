from pydantic import BaseModel, Field


class PolicyEvidence(BaseModel):
    """
    A single piece of evidence retrieved from a policy document.
    """

    chunk_id: str = Field(
        description="Unique identifier of the retrieved chunk."
    )

    document: str = Field(
        description="Source policy document filename."
    )

    page_number: int = Field(
        ge=1,
        description="Page number containing the evidence."
    )

    text: str = Field(
        description="Exact extracted text from the policy document."
    )

    score: float = Field(
        description="FAISS similarity score for the retrieval."
    )


class PolicyProfile(BaseModel):
    """
    Metadata describing the policy being used as the baseline.
    """

    provider: str

    product_name: str | None = None

    document: str

    evidence: list[PolicyEvidence] = Field(
        default_factory=list
    )