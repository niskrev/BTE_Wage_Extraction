# BTE_Wage_Extraction

Layout-aware deterministic extraction pipeline for mapping **Occupation -> Wage** relationships from BTE PDFs.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Scripts

### 1) Audit digital vs scanned files and target pages

```bash
python scripts/audit_pdfs.py --pdf-dir pdf --output artifacts/pdf_audit.json
```

### 2) Prototype parser over sample files

```bash
python scripts/prototype_parser.py --year 2024 --output artifacts/prototype_output.json
```

## Output schema

Records are validated with `Pydantic` via `WageRecord`:

- `pdf_id`
- `occupation_normalized`
- `occupation_raw`
- `wage_group_raw`
- `wage_amount` (> 500)
- `currency`
- `effective_year`
- `confidence_score`
- `extraction_method`
