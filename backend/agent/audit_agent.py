from agent.gemini_client import create_client, generate_content_with_retry
from models.audit import AuditReport, ClaimAudit
from models.pitch import PitchClaim, PitchContent
from rag.retrieval import search

from config import GEMINI_API_KEY, GEMINI_GENERATION_MODEL

def retrieve_claim_evidence(
    claim: str,
    index_dir: str,
    top_k: int = 3,
):
    """
    Independently retrieve policy evidence for a claim.

    This intentionally does NOT use the source_chunk_ids
    supplied by the pitch generator.
    """

    return search(
        query=claim,
        index_dir=index_dir,
        top_k=top_k,
    )


def format_evidence(results) -> str:
    """Format retrieved evidence for the audit model."""

    if not results:
        return "NO POLICY EVIDENCE FOUND."

    sections = []

    for index, result in enumerate(results, start=1):
        sections.append(
            f"""
EVIDENCE {index}
Chunk ID: {result.chunk_id}
Document: {result.document}
Page: {result.page_number}
Retrieval score: {result.score:.4f}

TEXT:
{result.text}
""".strip()
        )

    return "\n\n".join(sections)

def audit_claim(claim: PitchClaim, evidence: str) -> ClaimAudit:

    evidence_context = format_evidence(evidence)

    prompt = f"""
You are auditing a claim generated for a corporate
health-insurance presentation.

CLAIM:
{claim.claim}

CLAIM TYPE:
{claim.claim_type}

INDEPENDENTLY RETRIEVED POLICY EVIDENCE:
{evidence_context}

Determine whether the supplied policy evidence supports
the claim.

Use ONLY the supplied policy evidence.

Classify the claim as exactly one of:

supported
- The evidence directly supports the claim.

partially_supported
- The evidence supports part of the claim, but the claim
  contains additional unsupported or inaccurate information.

unsupported
- The evidence does not establish the claim.

IMPORTANT RULES:

1. Do not use outside knowledge.
2. Do not assume that a missing statement is true.
3. Do not treat semantic similarity alone as proof.
4. Pay attention to exact limits, durations, conditions,
   exclusions, and qualifiers.
5. If the claim says "unlimited", the evidence must actually
   establish unlimited coverage.
6. If the claim contains a monetary amount, verify that
   exact amount.
7. If the claim contains a duration, verify that exact
   duration.
8. If the evidence only partially supports a claim, use
   partially_supported.
9. Explain your decision concisely.
10. If supported, identify the strongest supporting evidence.
11. If unsupported, do not invent a source.

Return ONLY the structured ClaimAudit object.
"""

    client = create_client()

    response = generate_content_with_retry(
        client=client,
        model=GEMINI_GENERATION_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ClaimAudit,
        }
    )

    if not response.text:
        raise RuntimeError("empty audit response")

    result = ClaimAudit.model_validate_json(response.text)

    if result.status == "supported" and evidence:
        strongest = evidence[0]

        result.source_document = strongest.document
        result.source_page = strongest.page_number
        result.source_chunk_id = strongest.chunk_id
        result.evidence = strongest.text

    elif result.status == "partially_supported" and evidence:
        strongest = evidence[0]

        result.source_document = strongest.document
        result.source_page = strongest.page_number
        result.source_chunk_id = strongest.chunk_id
        result.evidence = strongest.text

    return result

def extract_claims(pitch: PitchContent) -> list[PitchClaim]:
    """Extract every claim from every slide."""

    claims: list[PitchClaim] = []

    for slide in pitch.slides:
        claims.extend(slide.claims)

    return claims

def audit_pitch(
    pitch: PitchContent,
    policy_index_dir: str,
    *,
    top_k: int = 3,
) -> AuditReport:
    """
    Independently audit every claim in a generated pitch
    against the selected policy's FAISS index.
    """

    claims = extract_claims(pitch)

    if not claims:
        return AuditReport(
            company_name=pitch.company_name,
            policy_provider=pitch.policy_provider,
            policy_product=pitch.policy_product,
            claims=[],
            total_claims=0,
            supported_claims=0,
            partially_supported_claims=0,
            unsupported_claims=0,
            audit_passed=True,
        )

    audits: list[ClaimAudit] = []

    for claim in claims:
        evidence = retrieve_claim_evidence(
            claim=claim.claim,
            index_dir=policy_index_dir,
            top_k=top_k,
        )

        audit = audit_claim(
            claim=claim,
            evidence=evidence,
        )

        audits.append(audit)

    supported = sum(
        audit.status == "supported"
        for audit in audits
    )

    partially_supported = sum(
        audit.status == "partially_supported"
        for audit in audits
    )

    unsupported = sum(
        audit.status == "unsupported"
        for audit in audits
    )

    return AuditReport(
        company_name=pitch.company_name,
        policy_provider=pitch.policy_provider,
        policy_product=pitch.policy_product,
        claims=audits,
        total_claims=len(audits),
        supported_claims=supported,
        partially_supported_claims=partially_supported,
        unsupported_claims=unsupported,
        audit_passed=unsupported == 0,
    )