#!/usr/bin/env python3
"""Validate source/claim JSONL records and their LaTeX claim references."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SOURCE_ID = re.compile(r"S\d{3,}")
CLAIM_ID = re.compile(r"C\d{3,}")
READ_DEPTHS = {"full", "partial", "metadata_only", "unreadable"}
CLAIM_KINDS = {
    "source_statement",
    "experiment_observation",
    "inference",
    "hypothesis",
    "insufficient_evidence",
}
CONFIDENCE = {"high", "medium", "low", "unknown"}

SOURCE_FIELDS = {
    "source_id",
    "title",
    "locator",
    "source_type",
    "publisher_or_author",
    "published_or_version",
    "accessed_at",
    "read_depth",
    "evidence_scope",
    "limitations",
}
CLAIM_FIELDS = {
    "claim_id",
    "claim",
    "kind",
    "source_ids",
    "locators",
    "confidence",
    "limitations",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report_dir", type=Path)
    parser.add_argument("--main-tex", type=Path)
    parser.add_argument("--require-claim-refs", action="store_true")
    parser.add_argument("--check-local-paths", action="store_true")
    return parser.parse_args()


def read_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.is_file():
        errors.append(f"Missing JSONL file: {path}")
        return records
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}:{line_number}: each line must be a JSON object")
            continue
        value["__line__"] = line_number
        records.append(value)
    return records


def missing_fields(record: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(field for field in required if field not in record)


def collect_tex_files(main_tex: Path, errors: list[str]) -> list[Path]:
    discovered: list[Path] = []
    queue = [main_tex.resolve()]
    seen: set[Path] = set()
    input_pattern = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        if not path.is_file():
            errors.append(f"TeX source not found: {path}")
            continue
        discovered.append(path)
        content = path.read_text(encoding="utf-8", errors="replace")
        for match in input_pattern.finditer(content):
            child = Path(match.group(1))
            if not child.suffix:
                child = child.with_suffix(".tex")
            queue.append((path.parent / child).resolve())
    return discovered


def main() -> int:
    args = parse_args()
    report_dir = args.report_dir.expanduser().resolve()
    main_tex = (args.main_tex or report_dir / "main.tex").expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    source_records = read_jsonl(report_dir / "evidence" / "sources.jsonl", errors)
    claim_records = read_jsonl(report_dir / "evidence" / "claims.jsonl", errors)
    if not source_records:
        errors.append("sources.jsonl contains no source records")
    if not claim_records:
        errors.append("claims.jsonl contains no claim records")

    sources: dict[str, dict[str, Any]] = {}
    for record in source_records:
        line = record.get("__line__")
        missing = missing_fields(record, SOURCE_FIELDS)
        if missing:
            errors.append(f"sources.jsonl:{line}: missing fields: {', '.join(missing)}")
            continue
        source_id = record["source_id"]
        if not isinstance(source_id, str) or not SOURCE_ID.fullmatch(source_id):
            errors.append(f"sources.jsonl:{line}: invalid source_id: {source_id!r}")
            continue
        if source_id in sources:
            errors.append(f"sources.jsonl:{line}: duplicate source_id: {source_id}")
            continue
        if record["read_depth"] not in READ_DEPTHS:
            errors.append(f"sources.jsonl:{line}: invalid read_depth: {record['read_depth']!r}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(record["accessed_at"])):
            errors.append(f"sources.jsonl:{line}: accessed_at must use YYYY-MM-DD")
        if args.check_local_paths:
            locator = str(record["locator"])
            candidate = Path(locator).expanduser()
            if candidate.is_absolute() and not candidate.exists():
                errors.append(f"sources.jsonl:{line}: local locator does not exist: {locator}")
        sources[source_id] = record

    claims: dict[str, dict[str, Any]] = {}
    used_source_ids: set[str] = set()
    for record in claim_records:
        line = record.get("__line__")
        missing = missing_fields(record, CLAIM_FIELDS)
        if missing:
            errors.append(f"claims.jsonl:{line}: missing fields: {', '.join(missing)}")
            continue
        claim_id = record["claim_id"]
        if not isinstance(claim_id, str) or not CLAIM_ID.fullmatch(claim_id):
            errors.append(f"claims.jsonl:{line}: invalid claim_id: {claim_id!r}")
            continue
        if claim_id in claims:
            errors.append(f"claims.jsonl:{line}: duplicate claim_id: {claim_id}")
            continue
        kind = record["kind"]
        if kind not in CLAIM_KINDS:
            errors.append(f"claims.jsonl:{line}: invalid kind: {kind!r}")
        if record["confidence"] not in CONFIDENCE:
            errors.append(f"claims.jsonl:{line}: invalid confidence: {record['confidence']!r}")
        source_ids = record["source_ids"]
        locators = record["locators"]
        if not isinstance(source_ids, list) or not all(isinstance(item, str) for item in source_ids):
            errors.append(f"claims.jsonl:{line}: source_ids must be an array of strings")
            source_ids = []
        if not isinstance(locators, list) or not all(isinstance(item, str) for item in locators):
            errors.append(f"claims.jsonl:{line}: locators must be an array of strings")
            locators = []
        for source_id in source_ids:
            used_source_ids.add(source_id)
            if source_id not in sources:
                errors.append(f"claims.jsonl:{line}: unknown source_id: {source_id}")

        if kind == "source_statement":
            if not source_ids or not locators:
                errors.append(f"claims.jsonl:{line}: source_statement needs source_ids and locators")
            readable = [
                source_id
                for source_id in source_ids
                if source_id in sources and sources[source_id].get("read_depth") in {"full", "partial"}
            ]
            if source_ids and not readable:
                errors.append(
                    f"claims.jsonl:{line}: source_statement has no full/partial readable source"
                )
        elif kind == "experiment_observation":
            if not record.get("observation_artifact"):
                errors.append(f"claims.jsonl:{line}: experiment_observation needs observation_artifact")
        elif kind == "inference":
            if not source_ids and not record.get("observation_artifact"):
                errors.append(f"claims.jsonl:{line}: inference needs a source or observation_artifact")
        elif kind == "hypothesis":
            if not record.get("validation"):
                errors.append(f"claims.jsonl:{line}: hypothesis needs validation")
        elif kind == "insufficient_evidence":
            if not str(record.get("limitations", "")).strip():
                errors.append(f"claims.jsonl:{line}: insufficient_evidence needs limitations")
        claims[claim_id] = record

    for source_id in sorted(set(sources) - used_source_ids):
        warnings.append(f"Source is not used by any claim: {source_id}")

    tex_files = collect_tex_files(main_tex, errors)
    tex_content = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in tex_files)
    referenced_claims = set(re.findall(r"\\claimref\s*\{(C\d{3,})\}", tex_content))
    for claim_id in sorted(referenced_claims - set(claims)):
        errors.append(f"LaTeX references unknown claim: {claim_id}")
    if args.require_claim_refs:
        for claim_id in sorted(set(claims) - referenced_claims):
            errors.append(f"Claim is not referenced from LaTeX: {claim_id}")
        if claims and not referenced_claims:
            errors.append("No \\claimref{...} markers found in LaTeX")

    result = {
        "status": "valid" if not errors else "invalid",
        "report_dir": str(report_dir),
        "source_count": len(sources),
        "claim_count": len(claims),
        "referenced_claim_count": len(referenced_claims),
        "tex_files": [str(path) for path in tex_files],
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

