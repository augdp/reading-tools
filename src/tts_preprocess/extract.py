from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


def extract_pages(pdf_path: str | Path, page_indexes: list[int]) -> str:
    """
    Extract selected PDF pages and return one plain text string.

    Args:
        pdf_path: Path to the PDF file.
        page_indexes: Zero-based page indexes.

    Example:
        extract_pages("book.pdf", [0, 1, 2])
        extracts human pages 1, 2, and 3.
    """
    pages = extract_pages_with_numbers(pdf_path, page_indexes)

    chunks = []

    for page in pages:
        text = page.text.strip()

        if text:
            chunks.append(text)

    if not chunks:
        return ""

    return "\n\n".join(chunks).strip() + "\n"


def extract_pages_with_numbers(
    pdf_path: str | Path,
    page_indexes: list[int],
) -> list[ExtractedPage]:
    """
    Extract selected PDF pages while preserving their human page numbers.

    Human page number means:
        zero-based index 0 -> page_number 1
        zero-based index 1 -> page_number 2
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if not pdf_path.is_file():
        raise ValueError(f"Path is not a file: {pdf_path}")

    if not page_indexes:
        raise ValueError("At least one page must be selected.")

    extracted_pages: list[ExtractedPage] = []

    with fitz.open(pdf_path) as document:
        page_count = document.page_count

        for page_index in page_indexes:
            if page_index < 0:
                raise ValueError(f"Invalid page index: {page_index}")

            if page_index >= page_count:
                human_page = page_index + 1
                raise ValueError(
                    f"Page {human_page} does not exist. "
                    f"The PDF has {page_count} page(s)."
                )

            page = document.load_page(page_index)

            text = page.get_text("text", sort=True)

            extracted_pages.append(
                ExtractedPage(
                    page_number=page_index + 1,
                    text=text,
                )
            )

    return extracted_pages
