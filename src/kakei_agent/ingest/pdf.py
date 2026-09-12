from pathlib import Path

import pymupdf


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Extract all text from a PDF while preserving page boundaries.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text from all pages.

    Raises:
        FileNotFoundError: If the PDF does not exist.
        ValueError: If the file is not a PDF.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {pdf_path}")

    pages: list[str] = []

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text")

            pages.append(
                f"--- PAGE {page_number} ---\n"
                f"{text.strip()}"
            )

    return "\n\n".join(pages)