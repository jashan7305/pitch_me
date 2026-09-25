from dataclasses import dataclass
from pathlib import Path

from rag.extraction import PageContent

@dataclass
class Chunk:
    chunk_id: str
    document: str
    page_number: int
    text: str

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 100

def _split_text(text: str) -> list[str]:
    """
    Split a page's text into overlapping chunks.

    Splitting prefers natural boundaries:
    paragraphs -> lines -> sentences -> words.
    """

    text = text.strip()

    if not text:
        return []

    if len(text) <= CHUNK_SIZE:
        return [text]

    # Try increasingly fine-grained separators.
    separators = ["\n\n", "\n", ". ", " ", ""]

    chunks: list[str] = []

    def split_recursive(value: str, separator_index: int) -> list[str]:
        if len(value) <= CHUNK_SIZE:
            return [value]

        if separator_index >= len(separators):
            return [
                value[i : i + CHUNK_SIZE]
                for i in range(0, len(value), CHUNK_SIZE)
            ]

        separator = separators[separator_index]

        if not separator:
            return [
                value[i : i + CHUNK_SIZE]
                for i in range(0, len(value), CHUNK_SIZE)
            ]

        parts = value.split(separator)

        if len(parts) == 1:
            return split_recursive(value, separator_index + 1)

        result: list[str] = []
        current = ""

        for part in parts:
            part = part.strip()

            if not part:
                continue

            candidate = (
                f"{current}{separator}{part}"
                if current
                else part
            )

            if len(candidate) <= CHUNK_SIZE:
                current = candidate
            else:
                if current:
                    result.append(current)

                # A single section can itself be too large.
                if len(part) > CHUNK_SIZE:
                    result.extend(
                        split_recursive(
                            part,
                            separator_index + 1,
                        )
                    )
                    current = ""
                else:
                    current = part

        if current:
            result.append(current)

        return result

    raw_chunks = split_recursive(text, 0)

    # Add overlap between neighboring chunks.
    for index, chunk in enumerate(raw_chunks):
        if index == 0:
            chunks.append(chunk)
            continue

        previous = raw_chunks[index - 1]

        overlap = previous[-CHUNK_OVERLAP:]

        chunks.append(
            f"{overlap} {chunk}".strip()
        )

    return chunks

def chunk_pages(
    pages: list[PageContent],
    document_name: str | Path,
) -> list[Chunk]:
    """
    Convert page-level extracted text into retrieval chunks.

    Each chunk retains:
    - unique ID
    - document name
    - page number
    - chunk text

    Chunks never cross page boundaries.
    """

    document_name = Path(document_name).name

    chunks: list[Chunk] = []

    for page in pages:
        if not page.text.strip():
            continue

        page_chunks = _split_text(page.text)

        for chunk_index, text in enumerate(page_chunks):
            chunks.append(
                Chunk(
                    chunk_id=f"{document_name}:p{page.page_number}:c{chunk_index}",
                    document=document_name,
                    page_number=page.page_number,
                    text=text,
                )
            )

    return chunks


