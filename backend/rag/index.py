import json
from pathlib import Path

import faiss
import numpy as np

from rag.chunking import Chunk

INDEX_FILENAME = "index.faiss"
METADATA_FILENAME = "metadata.json"

def normalize_embeddings(embeddings: list[list[float]]) -> np.ndarray:

    if not embeddings:
        raise ValueError("empty embeddings")

    vectors = np.asarray(embeddings, dtype=np.float32)
    faiss.normalize_L2(vectors)
    return vectors

def build_index(
        chunks: list[Chunk],
        embeddings: list[list[float]],
        output_dir: str | Path
) -> None:

    if not chunks:
        raise ValueError("empty chunks")
    if not embeddings:
        raise ValueError("empty embeddings")
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings must have the same length")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    vectors = normalize_embeddings(embeddings)
    dimension = vectors.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(vectors)

    index_path = output_dir / INDEX_FILENAME
    metadata_path = output_dir / METADATA_FILENAME

    faiss.write_index(index, str(index_path))

    metadata = [
        {
            "chunk_id": chunk.chunk_id,
            "document": chunk.document,
            "page_number": chunk.page_number,
            "text": chunk.text,
        }
        for chunk in chunks
    ]
    metadata_path.write_text(
        json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

def load_index(
    index_dir: str | Path,
) -> tuple[faiss.Index, list[dict]]:
    """
    Load a persisted FAISS index and its metadata.
    """

    index_dir = Path(index_dir)

    index_path = index_dir / INDEX_FILENAME
    metadata_path = index_dir / METADATA_FILENAME

    if not index_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {index_path}"
        )

    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {metadata_path}"
        )

    index = faiss.read_index(
        str(index_path)
    )

    metadata = json.loads(
        metadata_path.read_text(
            encoding="utf-8"
        )
    )

    if index.ntotal != len(metadata):
        raise ValueError(
            f"Index/metadata mismatch: "
            f"{index.ntotal} vectors vs {len(metadata)} metadata entries"
        )

    return index, metadata