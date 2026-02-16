from __future__ import annotations

import re
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    import pandas as pd

JOIN_KEY_CANDIDATES = ("nível", "nivel", "grupo", "índice", "indice", "escalão", "escalao")

ROMAN_MAP = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
    "VIII": 8,
    "IX": 9,
    "X": 10,
}


def normalize_join_value(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(value)).strip().upper()
    if cleaned in ROMAN_MAP:
        return str(ROMAN_MAP[cleaned])
    return cleaned.replace("NÍVEL", "NIVEL").replace("ÍNDICE", "INDICE")


def parse_eur_amount(value: str) -> float | None:
    text = str(value).replace("€", "").replace(" ", "").strip()
    if not text:
        return None
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def _find_matching_column(columns: Iterable[str]) -> str | None:
    lowered = {str(col).strip().lower(): col for col in columns}
    for key in JOIN_KEY_CANDIDATES:
        if key in lowered:
            return str(lowered[key])
    return None


def link_category_and_wage_tables(category_df: "pd.DataFrame", wage_df: "pd.DataFrame") -> "pd.DataFrame":
    import pandas as pd

    category_key = _find_matching_column(category_df.columns)
    wage_key = _find_matching_column(wage_df.columns)
    if not category_key or not wage_key:
        return pd.DataFrame()

    category_work = category_df.copy()
    wage_work = wage_df.copy()
    category_work["_join_key"] = category_work[category_key].map(normalize_join_value)
    wage_work["_join_key"] = wage_work[wage_key].map(normalize_join_value)

    merged = category_work.merge(wage_work, on="_join_key", suffixes=("_category", "_wage"))
    return merged
