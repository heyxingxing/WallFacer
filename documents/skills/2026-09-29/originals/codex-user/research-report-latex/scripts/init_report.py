#!/usr/bin/env python3
"""Initialize a non-overwriting LaTeX research-report workspace."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path


TOKEN_MAP = {
    "title": "__REPORT_TITLE__",
    "subtitle": "__REPORT_SUBTITLE__",
    "author": "__REPORT_AUTHOR__",
    "date": "__REPORT_DATE__",
    "scope": "__REPORT_SCOPE__",
}


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--title", required=True, help="Plain-text report title")
    parser.add_argument("--subtitle", default="研究问题、证据与结论")
    parser.add_argument("--author", default="资料整理者")
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--scope", default="按用户指定资料与版本整理")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        raise SystemExit("--date must use YYYY-MM-DD")

    output_dir = args.output_dir.expanduser().resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty directory: {output_dir}")

    template_dir = Path(__file__).resolve().parent.parent / "assets" / "report-template"
    if not template_dir.is_dir():
        raise SystemExit(f"Template directory not found: {template_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    values = {
        "title": args.title,
        "subtitle": args.subtitle,
        "author": args.author,
        "date": args.date,
        "scope": args.scope,
    }

    created: list[str] = []
    for source in sorted(template_dir.iterdir()):
        destination = output_dir / source.name
        if source.suffix in {".tex", ".bib", ".md", ".txt"}:
            content = source.read_text(encoding="utf-8")
            for key, token in TOKEN_MAP.items():
                content = content.replace(token, latex_escape(values[key]))
            destination.write_text(content, encoding="utf-8")
        else:
            shutil.copy2(source, destination)
        created.append(str(destination))

    evidence_dir = output_dir / "evidence"
    figures_dir = output_dir / "figures"
    evidence_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)
    for filename in ("sources.jsonl", "claims.jsonl"):
        path = evidence_dir / filename
        path.write_text("", encoding="utf-8")
        created.append(str(path))

    result = {
        "status": "initialized",
        "output_dir": str(output_dir),
        "created": created,
        "next": [
            "Populate evidence/sources.jsonl and evidence/claims.jsonl",
            "Replace every \\ReportPlaceholder in the TeX sources",
            "Run validate_evidence.py before compiling",
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

