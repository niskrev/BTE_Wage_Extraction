from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .extraction import extract_tables
from .ingestion import PDFProfile, build_pdf_profile
from .linking import JOIN_KEY_CANDIDATES, link_category_and_wage_tables, parse_eur_amount
from .schema import WageRecord


@dataclass(slots=True)
class PipelineResult:
    profile: PDFProfile
    records: list[WageRecord]


def _score_record(wage_amount: float, method: str, matched_exactly: bool) -> float:
    if method == "deterministic_lattice" and matched_exactly and wage_amount > 500:
        return 1.0
    if wage_amount > 500:
        return 0.85
    return 0.5


def _pick_column(columns: list[str], preferred_tokens: tuple[str, ...]) -> str | None:
    for column in columns:
        lowered = str(column).lower()
        if any(token in lowered for token in preferred_tokens):
            return column
    return None


def _build_records_from_join(pdf_id: str, merged: pd.DataFrame, method: str, year: int) -> list[WageRecord]:
    occupation_col = _pick_column(list(merged.columns), ("categoria", "profissão", "profissao", "ocupação", "ocupacao"))
    group_col = _pick_column(list(merged.columns), JOIN_KEY_CANDIDATES)
    wage_col = _pick_column(list(merged.columns), ("remun", "sal", "euros", "€", "retribuição", "retribuicao", "valor"))

    if not occupation_col or not group_col or not wage_col:
        return []

    records: list[WageRecord] = []
    for row in merged.to_dict(orient="records"):
        wage = parse_eur_amount(row.get(wage_col, ""))
        if wage is None or wage <= 500:
            continue

        occupation_raw = str(row.get(occupation_col, "")).strip()
        if not occupation_raw:
            continue

        records.append(
            WageRecord(
                pdf_id=pdf_id,
                occupation_normalized=occupation_raw,
                occupation_raw=occupation_raw,
                wage_group_raw=str(row.get(group_col, "")).strip(),
                wage_amount=wage,
                currency="EUR",
                effective_year=year,
                confidence_score=_score_record(wage, method, matched_exactly=True),
                extraction_method=method,
            )
        )
    return records


def run_pipeline_for_pdf(pdf_path: Path, effective_year: int) -> PipelineResult:
    profile = build_pdf_profile(pdf_path)
    tables, method = extract_tables(profile.pdf_path, profile.page_indices, profile.file_type)
    records: list[WageRecord] = []

    if len(tables) >= 2:
        merged = link_category_and_wage_tables(tables[0], tables[1])
        if not merged.empty:
            records = _build_records_from_join(profile.pdf_id, merged, method, effective_year)

    return PipelineResult(profile=profile, records=records)
