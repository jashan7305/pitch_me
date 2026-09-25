from agent.gemini_client import create_client, generate_content_with_retry
from models.company import CompanyProfile
from models.policy import PolicyProfile
from models.pitch import PitchContent

from config import GEMINI_API_KEY, GEMINI_GENERATION_MODEL

def format_policy_evidence(policy: PolicyProfile) -> str:

    sections: list[str] = []
    for index, evidence in enumerate(policy.evidence, start=1):
        sections.append(
            f"""
EVIDENCE {index}
Chunk ID: {evidence.chunk_id}
Document: {evidence.document}
Page: {evidence.page_number}
Retrieval score: {evidence.score:.4f}

TEXT:
{evidence.text}
""".strip()
        )

    return "\n\n".join(sections)

def generate_pitch(company: CompanyProfile, policy: PolicyProfile) -> PitchContent:

    company_context = company.model_dump_json(
        indent=2
    )
    policy_evidence = format_policy_evidence(
        policy
    )

    prompt = f"""
You are a corporate insurance advisor preparing a
client-specific marketing pitch.

CLIENT COMPANY:
{company.company_name}

SELECTED POLICY:
Provider: {policy.provider}
Product: {policy.product_name or "Not specified"}
Document: {policy.document}

COMPANY PROFILE:
{company_context}

RETRIEVED POLICY EVIDENCE:
{policy_evidence}

Your task is to create a concise 5 slide pitch
for the client.

GROUNDING RULES:

1. The selected policy is the only policy you may discuss.

2. The selected policy is:
   {policy.provider} {policy.product_name or ""}

3. Do not introduce or recommend another insurer or policy.

4. Use ONLY the supplied policy evidence for policy facts.

5. Never invent:
   - coverage
   - limits
   - exclusions
   - waiting periods
   - eligibility requirements
   - pricing
   - claim conditions
   - policy terms

6. If a policy fact cannot be supported by the supplied
   evidence, do not state it as a fact.

7. Company facts must come from the supplied CompanyProfile.

8. Do not invent company facts.

9. Clearly distinguish company facts from insurance
   inferences.

10. An inference about what may be useful to the client
    must not be presented as a documented policy fact.

11. Every policy-related claim must include the relevant
    evidence chunk ID in source_chunk_ids.

12. Keep slide content concise and suitable for a
    professional client presentation.

13. Do not include citations or URLs in the visible
    slide text unless they are explicitly needed.

14. The final slide must contain the recommendation for
    the selected policy and a concise rationale based on
    the client's identified exposures and the supplied
    policy evidence.

RECOMMENDED STRUCTURE:

Slide 1:
Client context and key employee/insurance needs.

Slide 2:
Relevant policy benefits supported by the evidence.

Slide 3:
How the documented policy benefits address the
client's identified needs.

Slide 4:
Additional relevant policy features or considerations,
only if supported by evidence.

Slide 5:
Final recommendation and rationale.

Use 3 slides if that is sufficient.
Use 4 or 5 only when the additional content is useful.

IMPORTANT:

The recommendation is about the selected policy only.
Do not compare it against policies that were not supplied.

Return ONLY the structured PitchContent object.
"""

    client = create_client()

    response = generate_content_with_retry(
        client=client,
        model=GEMINI_GENERATION_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": PitchContent,
        }
    )
    if not response.text:
        raise RuntimeError("empty pitch response")

    return PitchContent.model_validate_json(response.text)
