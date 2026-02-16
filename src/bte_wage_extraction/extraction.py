from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import pandas as pd


def _load_optional_module(module_name: str) -> Any | None:
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return None
    return importlib.import_module(module_name)


def extract_tables_digital(pdf_path: Path, page_indices: list[int]) -> list[pd.DataFrame]:
    """Extract tables from digital PDFs using Camelot first, then pdfplumber fallback."""
    tables: list[pd.DataFrame] = []
    camelot = _load_optional_module("camelot")

    if camelot is not None and page_indices:
        pages_arg = ",".join(str(page + 1) for page in page_indices)
        lattice_result = camelot.read_pdf(str(pdf_path), pages=pages_arg, flavor="lattice")
        stream_result = camelot.read_pdf(str(pdf_path), pages=pages_arg, flavor="stream")
        tables.extend(table.df for table in lattice_result)
        tables.extend(table.df for table in stream_result)

    if tables:
        return tables

    pdfplumber = _load_optional_module("pdfplumber")
    if pdfplumber is None:
        return tables

    with pdfplumber.open(str(pdf_path)) as pdf:
        for index in page_indices:
            page = pdf.pages[index]
            extracted = page.extract_tables()
            for rows in extracted:
                if rows:
                    table_df = pd.DataFrame(rows[1:], columns=rows[0])
                    tables.append(table_df)
    return tables


def extract_tables_ocr(pdf_path: Path, page_indices: list[int]) -> list[pd.DataFrame]:
    """OCR fallback for scanned PDFs. Returns a simple text-block dataframe per page."""
    paddleocr = _load_optional_module("paddleocr")
    fitz = _load_optional_module("fitz")
    if paddleocr is None or fitz is None:
        return []

    ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang="pt")
    tables: list[pd.DataFrame] = []
    with fitz.open(pdf_path) as document:
        for page_index in page_indices:
            page = document[page_index]
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image_path = pdf_path.with_suffix(f".page{page_index}.png")
            pixmap.save(image_path)
            result = ocr.ocr(str(image_path), cls=True)
            rows = []
            for block in result[0] if result else []:
                text = block[1][0]
                score = block[1][1]
                rows.append({"text": text, "ocr_score": score})
            if rows:
                tables.append(pd.DataFrame(rows))
            image_path.unlink(missing_ok=True)
    return tables


def extract_tables(pdf_path: Path, page_indices: list[int], file_type: str) -> tuple[list[pd.DataFrame], str]:
    """Return extracted tables and method used."""
    if file_type == "digital":
        tables = extract_tables_digital(pdf_path, page_indices)
        if tables:
            return tables, "deterministic_lattice"
    tables = extract_tables_ocr(pdf_path, page_indices)
    method = "ocr_paddle" if tables else "none"
    return tables, method
