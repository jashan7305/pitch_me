from dataclasses import dataclass
from pathlib import Path

import faiss

import numpy as np

from rag.embeddings import embed_query
from rag.index import load_index
from models.policy import PolicyEvidence
from models.company import CompanyProfile
from models.policy import PolicyEvidence, PolicyProfile

@dataclass
class RetrievalResult:
    chunk_id: str
    document: str
    page_number: int
    text: str
    score: float

def search(query: str, index_dir: str | Path, top_k: int = 3) -> list[RecursionError]:
    if not query:
        raise ValueError("empty query")

    index, metadata = load_index(index_dir=index_dir)

    top_k = min(top_k, index.ntotal)

    query_embedding = embed_query(query=query)
    query_vector = np.asarray([query_embedding], dtype=np.float32)
    faiss.normalize_L2(query_vector)

    scores, indices = index.search(query_vector, top_k)

    results: list[RetrievalResult] = []

    for score, index_id in zip(scores[0], indices[0]):
        if index_id < 0:
            continue
        item = metadata[index_id]
        results.append(
            RetrievalResult(
                chunk_id=item["chunk_id"],
                document=item["document"],
                page_number=item["page_number"],
                text=item["text"],
                score=float(score),
            )
        )
        
    return results

def retrieve_policy_evidence(query: str, index_dir: str | Path, top_k: int = 3) -> list[PolicyEvidence]:
    results = search(query=query, index_dir=index_dir, top_k=top_k)

    return [
        PolicyEvidence(
            chunk_id=result.chunk_id,
            document=result.document,
            page_number=result.page_number,
            text=result.text,
            score=result.score,
        )
        for result in results
    ]

def _build_exposure_queries(
    company: CompanyProfile,
) -> list[str]:
    """
    Convert company insurance exposures into retrieval queries.

    The queries are intentionally based on insurance exposures,
    rather than simply searching using the company name.
    """

    queries: list[str] = []

    for exposure in company.insurance_exposures:
        queries.append(
            exposure.exposure
        )

        queries.append(
            f"{exposure.exposure} "
            f"{exposure.rationale}"
        )

    return queries

def build_policy_profile(
    company: CompanyProfile,
    provider: str,
    document: str,
    product_name: str | None,
    index_dir: str | Path,
    *,
    top_k_per_query: int = 3,
) -> PolicyProfile:
    """
    Retrieve policy evidence relevant to the company's
    insurance exposures.

    All retrieval is restricted to the selected policy index.
    """

    queries = _build_exposure_queries(company)

    if not queries:
        raise ValueError(
            "Company profile contains no insurance exposures"
        )

    evidence_by_chunk: dict[str, PolicyEvidence] = {}

    for query in queries:
        results = retrieve_policy_evidence(
            query=query,
            index_dir=index_dir,
            top_k=top_k_per_query,
        )

        for result in results:
            existing = evidence_by_chunk.get(
                result.chunk_id
            )

            # If the same chunk was retrieved by multiple
            # queries, keep the highest similarity score.
            if (
                existing is None
                or result.score > existing.score
            ):
                evidence_by_chunk[result.chunk_id] = result

    evidence = sorted(
        evidence_by_chunk.values(),
        key=lambda item: item.score,
        reverse=True,
    )

    return PolicyProfile(
        provider=provider,
        product_name=product_name,
        document=document,
        evidence=evidence,
    )