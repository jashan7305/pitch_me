from __future__ import annotations

from google import genai
from google.genai import types

from rag.chunking import Chunk

from config import GEMINI_API_KEY, GEMINI_EMBEDDING_MODEL


def create_client() -> genai.Client:
    """Create a Gemini API client."""
    return genai.Client(api_key=GEMINI_API_KEY)


def embed_texts(
    texts: list[str],
    *,
    task_type: str,
) -> list[list[float]]:
    """
    Generate Gemini embeddings for a list of texts.

    task_type should be:
    - RETRIEVAL_DOCUMENT for policy chunks
    - RETRIEVAL_QUERY for search queries
    """

    if not texts:
        return []

    client = create_client()

    response = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        
        contents=texts,
        config=types.EmbedContentConfig(
            output_dimensionality=768,
            task_type=task_type,
        ),
    )

    return [
        embedding.values
        for embedding in response.embeddings
    ]


def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    """
    Generate embeddings for policy document chunks.

    Every chunk is embedded using RETRIEVAL_DOCUMENT
    because these vectors will be stored in the FAISS index.
    """

    texts = [chunk.text for chunk in chunks]

    return embed_texts(
        texts,
        task_type="RETRIEVAL_DOCUMENT",
    )


def embed_query(query: str) -> list[float]:
    """
    Generate an embedding for a retrieval query.

    Queries use RETRIEVAL_QUERY, which is specifically
    optimized for searching document embeddings.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty")

    embeddings = embed_texts(
        [query],
        task_type="RETRIEVAL_QUERY",
    )

    return embeddings[0]