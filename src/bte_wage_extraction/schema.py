from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class WageRecord(BaseModel):
    pdf_id: str
    occupation_normalized: str
    occupation_raw: str
    wage_group_raw: str
    wage_amount: float = Field(gt=500)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    effective_year: int = Field(ge=1990, le=2100)
    confidence_score: float = Field(ge=0.0, le=1.0)
    extraction_method: str

    @field_validator("occupation_normalized", "occupation_raw", "wage_group_raw")
    @classmethod
    def non_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Value must not be blank")
        return value.strip()


class WageRecordBatch(BaseModel):
    records: list[WageRecord]
