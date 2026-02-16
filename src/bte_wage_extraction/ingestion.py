from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz

KEYWORDS = (
    "tabela salarial",
    "remunerações",
    "remuneracoes",
    "categorias profissionais",
    "anexo",
)


@dataclass(slots=True)
class PDFProfile:
    pdf_path: Path
    pdf_id: str
    file_type: str
    page_indices: list[int]


def classify_pdf_type(pdf_path: Path, text_threshold: int = 60) -> str:
    """Classify PDF as born-digital or scanned by counting extractable text chars."""
    with fitz.open(pdf_path) as document:
        text_chars = sum(len(page.get_text("text").strip()) for page in document)
    return "digital" if text_chars >= text_threshold else "scanned"


def find_relevant_pages(pdf_path: Path, expansion: int = 1) -> list[int]:
    """Return page indices likely containing wage/category information."""
    matches: set[int] = set()
    with fitz.open(pdf_path) as document:
        for index, page in enumerate(document):
            content = page.get_text("text").lower()
            if any(keyword in content for keyword in KEYWORDS):
                start = max(0, index - expansion)
                end = min(len(document) - 1, index + expansion)
                matches.update(range(start, end + 1))
    return sorted(matches)


def build_pdf_profile(pdf_path: Path) -> PDFProfile:
    return PDFProfile(
        pdf_path=pdf_path,
        pdf_id=pdf_path.stem,
        file_type=classify_pdf_type(pdf_path),
        page_indices=find_relevant_pages(pdf_path),
    )


def audit_pdf_directory(pdf_dir: Path) -> list[PDFProfile]:
    return [build_pdf_profile(path) for path in sorted(pdf_dir.glob("*.pdf"))]
