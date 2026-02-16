from __future__ import annotations

import argparse
import json
from pathlib import Path

from bte_wage_extraction.ingestion import audit_pdf_directory


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit PDFs as digital/scanned and identify relevant pages.")
    parser.add_argument("--pdf-dir", type=Path, default=Path("pdf"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/pdf_audit.json"))
    args = parser.parse_args()

    profiles = audit_pdf_directory(args.pdf_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    payload = [
        {
            "pdf_id": profile.pdf_id,
            "file_type": profile.file_type,
            "page_indices": profile.page_indices,
        }
        for profile in profiles
    ]
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote audit for {len(payload)} files to {args.output}")


if __name__ == "__main__":
    main()
