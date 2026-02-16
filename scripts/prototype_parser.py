from __future__ import annotations

import argparse
import json
from pathlib import Path

from bte_wage_extraction.pipeline import run_pipeline_for_pdf


def main() -> None:
    parser = argparse.ArgumentParser(description="Run prototype parser over sample BTE PDFs.")
    parser.add_argument("--pdfs", nargs="+", default=["pdf/00430074.pdf", "pdf/00750165.pdf", "pdf/00950108.pdf", "pdf/02430247.pdf"])
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--output", type=Path, default=Path("artifacts/prototype_output.json"))
    args = parser.parse_args()

    all_records = []
    for pdf in args.pdfs:
        result = run_pipeline_for_pdf(Path(pdf), effective_year=args.year)
        all_records.extend(record.model_dump() for record in result.records)
        print(f"{result.profile.pdf_id}: type={result.profile.file_type}, pages={result.profile.page_indices}, records={len(result.records)}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(all_records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(all_records)} records to {args.output}")


if __name__ == "__main__":
    main()
