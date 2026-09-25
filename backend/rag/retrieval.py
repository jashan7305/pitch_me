from dataclasses import dataclass
from pathlib import Path

import faiss

import numpy as np

from rag.embeddings import embed_query
from rag.index import load_index

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