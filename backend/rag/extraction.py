from dataclasses import dataclass
from pathlib import Path

import pymupdf

@dataclass
class PageContent:
    page_number: int
    text: str

def extract_text_from_pdf(pdf_path: str | Path) -> list[PageContent]:

    """
    extract text from .pdf file
    """

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF: {pdf_path}")

    pages: list[PageContent] = []
    with pymupdf.open(pdf_path) as pdf:
        if pdf.page_count == 0:
            raise ValueError(f"PDF file is empty: {pdf_path}")
        for page_index, page in enumerate(pdf):
            pages.append(
                PageContent(
                    page_number=page_index + 1,
                    text=page.get_text("text").strip()
                )
            )

    return pages

def validate_extraction(pages: list[PageContent]) -> None:

    """
    validate extracted pages
    """

    if not pages:
        raise ValueError("No pages extracted from the PDF.")
    pages_with_text = sum(bool(page.text) for page in pages)
    if pages_with_text == 0:
        raise ValueError("All extracted pages are empty.")
