from pydantic import BaseModel, Field


class CompanyExposure(BaseModel):
    """
    An insurance-relevant exposure identified from public
    company information.

    The evidence field should contain the source/fact that
    led to identifying the exposure.
    """

    exposure: str = Field(
        description="Insurance-relevant employee or business exposure."
    )

    rationale: str = Field(
        description="Why this exposure is relevant to the company."
    )

    evidence: str = Field(
        description="Publicly sourced fact supporting the exposure."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that the exposure applies to the company."
    )


class CompanyProfile(BaseModel):
    """
    Structured company profile used as input to the pitch agent.
    """

    company_name: str

    industry: str

    company_description: str

    employee_count: int | None = Field(
        default=None,
        ge=0,
        description="Estimated number of employees if publicly available."
    )

    employee_count_source: str | None = None

    headquarters: str | None = None

    operating_locations: list[str] = Field(
        default_factory=list
    )

    workforce_characteristics: list[str] = Field(
        default_factory=list,
        description=(
            "Relevant characteristics of the workforce, "
            "such as distributed workforce or large employee base."
        ),
    )

    insurance_exposures: list[CompanyExposure] = Field(
        default_factory=list
    )

    sources: list[str] = Field(
        default_factory=list,
        description="URLs or source references used to construct the profile."
    )