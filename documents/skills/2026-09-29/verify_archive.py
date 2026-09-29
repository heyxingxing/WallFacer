#!/usr/bin/env python3
"""Verify this archive's recorded bytes; this is not a skill-effectiveness test."""
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    errors = []
    expected = set()
    for line in (root / "SHA256SUMS").read_text().splitlines():
        digest, relative = line.split("  ", 1)
        path = root / relative
        expected.add(relative)
        if path.is_symlink() or not path.is_file():
            errors.append(f"Missing or symbolic file: {relative}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append(f"Checksum mismatch: {relative}")
    actual = {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    }
    if actual != expected:
        errors.append(f"Unexpected files: {sorted(actual - expected)}")
    manifest = json.loads((root / "manifest.json").read_text())
    for record in manifest["files"]:
        path = root / record["path"]
        if not path.is_file():
            errors.append(f"Missing provenance file: {record['path']}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != record["sha256"]:
            errors.append(f"Manifest mismatch: {record['path']}")
        if record["kind"] == "original" and digest != record["source_sha256"]:
            errors.append(f"Original-byte mismatch: {record['path']}")
    for package in manifest["packages"]:
        if not (root / package["path"] / "SKILL.md").is_file():
            errors.append(f"Missing entrypoint: {package['id']}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"PASS: {len(expected)} files, {len(manifest['packages'])} skill packages")


if __name__ == "__main__":
    main()
