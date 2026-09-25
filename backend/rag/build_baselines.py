from pathlib import Path

from rag.extraction import extract_text_from_pdf, validate_extraction
from rag.chunking import chunk_pages
from rag.embeddings import embed_chunks
from rag.index import build_index

from config import ABHI_DATA_DIR, CARE_DATA_DIR, HDFC_DATA_DIR, NIVA_DATA_DIR

BASELINE_PDF_PATHS = {
    ABHI_DATA_DIR: ABHI_DATA_DIR / "ABHI Product Brochure.pdf",
    CARE_DATA_DIR: CARE_DATA_DIR / "Care Health Product Brochure.pdf",
    HDFC_DATA_DIR: HDFC_DATA_DIR / "HDFC Product Brochure.pdf",
    NIVA_DATA_DIR: NIVA_DATA_DIR / "Niva Bupa Product Brochure.pdf"
}

def build_baseline(
        pdf_path: Path,
        output_dir: Path
) -> None:

    print(f"Building baseline for {pdf_path.name}...")

    # extraction
    pages = extract_text_from_pdf(pdf_path)
    validate_extraction(pages=pages)

    # chunking
    chunks = chunk_pages(pages=pages, document_name=pdf_path)

    # embedding
    embeddings = embed_chunks(chunks=chunks)

    # indexing
    build_index(
        chunks=chunks,
        embeddings=embeddings,
        output_dir=output_dir
    )

    print(f"Baseline built for {pdf_path.name} at {output_dir.resolve()}")

def main():
    for data_dir, pdf_path in BASELINE_PDF_PATHS.items():
        build_baseline(
            pdf_path=pdf_path,
            output_dir=data_dir
        )

if __name__ == "__main__":
    main()
