#!/usr/bin/env python3
"""Compile a LaTeX report in a fresh run directory and record PDF QA evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ENGINE_FLAGS = {
    "lualatex": "-lualatex",
    "xelatex": "-xelatex",
    "pdflatex": "-pdf",
}

FORBIDDEN_SOURCE_PATTERNS = {
    "ReportPlaceholder scaffold": re.compile(r"\\ReportPlaceholder\s*\{"),
    "verification marker": re.compile(r"\[VERIFY\]", re.IGNORECASE),
    "TODO marker": re.compile(r"\bTODO\b"),
    "tool citation token": re.compile(r"turn\d+(?:search|view|fetch|open)\d+|:codex-file-citation"),
}

CRITICAL_LOG_PATTERNS = {
    "LaTeX error": re.compile(r"(?:^|\n)! (?:LaTeX|Package .+?) Error:", re.MULTILINE),
    "undefined control sequence": re.compile(r"Undefined control sequence"),
    "emergency stop": re.compile(r"Emergency stop"),
    "fatal error": re.compile(r"Fatal error occurred"),
    "missing file": re.compile(r"(?:LaTeX Error: File|I can't find file).+", re.IGNORECASE),
    "missing font": re.compile(
        r"fontspec error|font .+ cannot be found|font .+ not loadable", re.IGNORECASE
    ),
}

STRICT_LOG_PATTERNS = {
    "undefined reference": re.compile(
        r"Reference .+ undefined|There were undefined references", re.IGNORECASE
    ),
    "undefined citation": re.compile(
        r"Citation .+ undefined|There were undefined citations", re.IGNORECASE
    ),
    "duplicate label": re.compile(
        r"Label .+ multiply defined|There were multiply-defined labels", re.IGNORECASE
    ),
    "rerun required": re.compile(
        r"Please \(re\)run Biber|Rerun to get cross-references right|rerun LaTeX", re.IGNORECASE
    ),
    "missing character": re.compile(r"Missing character:"),
    "overfull box": re.compile(r"Overfull \\hbox"),
}

NONBLOCKING_LOG_PATTERNS = {
    "underfull box": re.compile(r"Underfull \\hbox"),
    "overfull box": re.compile(r"Overfull \\hbox"),
    "package warning": re.compile(r"(?:Package .+ Warning|LaTeX(?: Font)? Warning):.+"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("main_tex", type=Path)
    parser.add_argument("--output", required=True, type=Path, help="Final PDF path")
    parser.add_argument(
        "--engine",
        choices=["auto", "lualatex", "xelatex", "pdflatex"],
        default="auto",
    )
    parser.add_argument("--tex-bin", type=Path, help="Existing TeX binary directory")
    parser.add_argument("--build-root", type=Path, help="Parent for append-only build runs")
    parser.add_argument("--qa-dir", type=Path, help="Directory for log, text, and build manifest")
    parser.add_argument("--render-dir", type=Path, help="Fresh directory for all page PNGs")
    parser.add_argument("--render-dpi", type=int, default=144)
    parser.add_argument("--expected-text", action="append", default=[])
    parser.add_argument("--report", type=Path, help="JSON build report path")
    parser.add_argument("--allow-latexmk-rc", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--timeout", type=int, default=300)
    return parser.parse_args()


def json_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def run_command(
    command: list[str], *, cwd: Path, env: dict[str, str], timeout: int
) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return completed.returncode, completed.stdout
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        return 124, f"{stdout}\nCommand timed out after {timeout} seconds."


def command_version(command: str | None, env: dict[str, str], cwd: Path) -> str | None:
    if not command:
        return None
    flag = (
        "-v"
        if Path(command).name in {"latexmk", "pdfinfo", "pdftotext", "pdffonts", "pdftoppm"}
        else "--version"
    )
    code, output = run_command([command, flag], cwd=cwd, env=env, timeout=30)
    if code not in {0, 1} and not output:
        return None
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return " | ".join(lines[:3]) if lines else None


def collect_tex_files(main_tex: Path) -> tuple[list[Path], list[str]]:
    errors: list[str] = []
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
    return discovered, errors


def source_preflight(tex_files: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in tex_files:
        content = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in FORBIDDEN_SOURCE_PATTERNS.items():
            for match in pattern.finditer(content):
                line = content.count("\n", 0, match.start()) + 1
                findings.append(f"{path}:{line}: {label}")
    return findings


def choose_engine(
    requested: str, source_text: str, available: dict[str, str | None]
) -> str | None:
    if requested != "auto":
        return requested if available.get(requested) else None

    magic = re.search(
        r"^\s*%\s*!TEX\s+program\s*=\s*(lua|xe|pdf)latex\s*$",
        source_text,
        re.IGNORECASE | re.MULTILINE,
    )
    if magic:
        magic_engine = magic.group(1).lower() + "latex"
        if available.get(magic_engine):
            return magic_engine

    if re.search(r"\\usepackage(?:\[[^]]*\])?\{xeCJK\}", source_text):
        return "xelatex" if available.get("xelatex") else None

    unicode_or_modern = bool(
        re.search(r"[\u2e80-\u9fff]", source_text)
        or re.search(r"\\(?:documentclass(?:\[[^]]*\])?\{ctex|usepackage\{fontspec\})", source_text)
    )
    if unicode_or_modern:
        for engine in ("lualatex", "xelatex"):
            if available.get(engine):
                return engine
        return None

    for engine in ("pdflatex", "lualatex", "xelatex"):
        if available.get(engine):
            return engine
    return None


def grep_log(content: str, patterns: dict[str, re.Pattern[str]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    lines = content.splitlines()
    for label, pattern in patterns.items():
        matches: list[str] = []
        for line in lines:
            if pattern.search(line):
                cleaned = line.strip()
                if cleaned and cleaned not in matches:
                    matches.append(cleaned)
        if not matches and pattern.search(content):
            matches.append(label)
        if matches:
            result[label] = matches[:100]
    return result


def parse_pdfinfo(output: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def parse_fonts(output: str) -> list[dict[str, str]]:
    row_pattern = re.compile(
        r"^(?P<name>\S+)\s{2,}(?P<type>.+?)\s{2,}(?P<encoding>\S+)\s+"
        r"(?P<embedded>yes|no)\s+(?P<subset>yes|no)\s+(?P<unicode>yes|no)\s+"
        r"(?P<object>\d+\s+\d+)$"
    )
    fonts: list[dict[str, str]] = []
    for line in output.splitlines():
        match = row_pattern.match(line.rstrip())
        if match:
            fonts.append(match.groupdict())
    return fonts


def normalized_text(value: str) -> str:
    return " ".join(value.split()).casefold()


def text_contains(haystack: str, needle: str) -> bool:
    normalized_haystack = normalized_text(haystack)
    normalized_needle = normalized_text(needle)
    if normalized_needle in normalized_haystack:
        return True
    compact_haystack = re.sub(r"\s+", "", haystack).casefold()
    compact_needle = re.sub(r"\s+", "", needle).casefold()
    return compact_needle in compact_haystack


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_atomic(source: Path, destination: Path, expected_sha256: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        shutil.copy2(source, temporary)
        copied_sha256 = sha256(temporary)
        if copied_sha256 != expected_sha256:
            raise OSError(
                "Atomic publication copy hash mismatch: "
                f"expected {expected_sha256}, got {copied_sha256}"
            )
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def main() -> int:
    args = parse_args()
    started_at = dt.datetime.now(dt.timezone.utc)
    main_tex = args.main_tex.expanduser().resolve()
    output_pdf = args.output.expanduser().resolve()
    qa_dir = args.qa_dir.expanduser().resolve() if args.qa_dir else output_pdf.parent
    report_path = (
        args.report or qa_dir / f"{output_pdf.stem}.build.json"
    ).expanduser().resolve()
    stable_log = qa_dir / f"{output_pdf.stem}.compile.log"
    text_output = qa_dir / f"{output_pdf.stem}.text.txt"

    errors: list[str] = []
    warnings: list[str] = []
    commands: list[list[str]] = []

    if main_tex.suffix.lower() != ".tex":
        errors.append(f"Main source must end in .tex: {main_tex}")
    if output_pdf.suffix.lower() != ".pdf":
        errors.append(f"Output must end in .pdf: {output_pdf}")
    if not main_tex.is_file():
        errors.append(f"Main TeX file not found: {main_tex}")

    render_dir = args.render_dir.expanduser().resolve() if args.render_dir else None
    if render_dir and render_dir.exists() and any(render_dir.iterdir()):
        errors.append(f"Render directory must be new or empty: {render_dir}")
    if args.strict and not render_dir:
        errors.append("Strict mode requires --render-dir for all-page visual QA")
    if args.strict and not args.expected_text:
        errors.append("Strict mode requires at least one --expected-text sentinel")

    env = dict(os.environ)
    tex_bin = args.tex_bin
    if tex_bin is None and env.get("LATEX_BIN_DIR"):
        tex_bin = Path(env["LATEX_BIN_DIR"])
    if tex_bin is not None:
        tex_bin = tex_bin.expanduser().resolve()
        if not tex_bin.is_dir():
            errors.append(f"TeX binary directory not found: {tex_bin}")
        else:
            env["PATH"] = str(tex_bin) + os.pathsep + env.get("PATH", "")

    tex_files: list[Path] = []
    source_text = ""
    if main_tex.is_file():
        tex_files, tex_errors = collect_tex_files(main_tex)
        errors.extend(tex_errors)
        source_text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace") for path in tex_files
        )
        preflight = source_preflight(tex_files)
        if preflight:
            target = errors if args.strict else warnings
            target.extend(preflight)

    executable_names = ["latexmk", "lualatex", "xelatex", "pdflatex", "biber"]
    executables = {name: shutil.which(name, path=env.get("PATH")) for name in executable_names}
    engine = choose_engine(args.engine, source_text, executables)
    if not executables["latexmk"]:
        errors.append("latexmk not found; use an existing TeX distribution via PATH or --tex-bin")
    if not engine:
        errors.append(f"No compatible engine found for --engine={args.engine}")

    build_root = (
        args.build_root.expanduser().resolve()
        if args.build_root
        else main_tex.parent / ".build"
    )
    run_id = started_at.strftime("%Y%m%dT%H%M%SZ") + f"-{os.getpid()}"
    run_dir = build_root / f"{main_tex.stem}-{run_id}"

    tool_versions = {
        name: command_version(path, env, main_tex.parent if main_tex.parent.exists() else Path.cwd())
        for name, path in executables.items()
        if path
    }
    for name in ("pdfinfo", "pdftotext", "pdffonts", "pdftoppm"):
        path = shutil.which(name, path=env.get("PATH"))
        executables[name] = path
        if path:
            tool_versions[name] = command_version(path, env, Path.cwd())

    report: dict[str, Any] = {
        "status": "failed",
        "started_at": started_at.isoformat(),
        "finished_at": None,
        "main_tex": str(main_tex),
        "tex_files": [str(path) for path in tex_files],
        "output_pdf": str(output_pdf),
        "qa_dir": str(qa_dir),
        "build_run_dir": str(run_dir),
        "render_dir": str(render_dir) if render_dir else None,
        "engine": engine,
        "strict": args.strict,
        "latexmk_rc_allowed": args.allow_latexmk_rc,
        "tool_versions": tool_versions,
        "commands": commands,
        "compile_exit_code": None,
        "log_findings": {},
        "pdf": {},
        "errors": errors,
        "warnings": warnings,
    }

    if errors:
        report["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        json_write(report_path, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    run_dir.mkdir(parents=True, exist_ok=False)
    latexmk_command = [str(executables["latexmk"])]
    if not args.allow_latexmk_rc:
        latexmk_command.append("-norc")
    latexmk_command.extend(
        [
            ENGINE_FLAGS[engine],
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            "-no-shell-escape",
            "-recorder",
            "-Werror",
            f"-outdir={run_dir}",
            main_tex.name,
        ]
    )
    commands.append(latexmk_command)
    compile_code, compile_output = run_command(
        latexmk_command, cwd=main_tex.parent, env=env, timeout=args.timeout
    )
    report["compile_exit_code"] = compile_code
    stdout_log = run_dir / "latexmk.stdout.log"
    stdout_log.write_text(compile_output, encoding="utf-8")

    generated_log = run_dir / f"{main_tex.stem}.log"
    log_content = generated_log.read_text(encoding="utf-8", errors="replace") if generated_log.is_file() else compile_output
    stable_log.parent.mkdir(parents=True, exist_ok=True)
    stable_log.write_text(log_content, encoding="utf-8")

    critical_findings = grep_log(log_content, CRITICAL_LOG_PATTERNS)
    strict_findings = grep_log(log_content, STRICT_LOG_PATTERNS)
    nonblocking_findings = grep_log(log_content, NONBLOCKING_LOG_PATTERNS)
    report["log_findings"] = {
        "critical": critical_findings,
        "strict": strict_findings,
        "nonblocking": nonblocking_findings,
    }

    if compile_code != 0:
        errors.append(f"latexmk exited with code {compile_code}")
    if critical_findings:
        errors.append("Final log contains critical LaTeX errors")
    if args.strict and strict_findings:
        errors.append("Final log contains strict-mode blocking findings")
    for label, lines in nonblocking_findings.items():
        warnings.append(f"{label}: {len(lines)} occurrence(s)")

    generated_pdf = run_dir / f"{main_tex.stem}.pdf"
    if not generated_pdf.is_file() or generated_pdf.stat().st_size == 0:
        errors.append(f"Generated PDF missing or empty: {generated_pdf}")

    candidate_sha256: str | None = None
    if not errors:
        candidate_sha256 = sha256(generated_pdf)
        report["pdf"]["candidate_sha256"] = candidate_sha256
        report["pdf"]["candidate_bytes"] = generated_pdf.stat().st_size

        pdfinfo_path = executables.get("pdfinfo")
        if pdfinfo_path:
            command = [str(pdfinfo_path), str(generated_pdf)]
            commands.append(command)
            code, info_output = run_command(command, cwd=main_tex.parent, env=env, timeout=60)
            report["pdf"]["pdfinfo_exit_code"] = code
            info = parse_pdfinfo(info_output)
            report["pdf"]["info"] = info
            try:
                pages = int(info.get("Pages", "0"))
            except ValueError:
                pages = 0
            report["pdf"]["pages"] = pages
            if code != 0 or pages <= 0:
                errors.append("pdfinfo could not confirm a positive page count")
            if info.get("Encrypted", "no").lower() != "no":
                errors.append("Final PDF is unexpectedly encrypted")
            if not info.get("Title"):
                warnings.append("PDF metadata has no Title")
        else:
            message = "pdfinfo not found; page count and encryption were not checked"
            (errors if args.strict else warnings).append(message)

        pdftotext_path = executables.get("pdftotext")
        extracted_text = ""
        if pdftotext_path:
            command = [str(pdftotext_path), "-layout", "-enc", "UTF-8", str(generated_pdf), str(text_output)]
            commands.append(command)
            code, tool_output = run_command(command, cwd=main_tex.parent, env=env, timeout=60)
            report["pdf"]["pdftotext_exit_code"] = code
            if code == 0 and text_output.is_file():
                extracted_text = text_output.read_text(encoding="utf-8", errors="replace")
            report["pdf"]["text_characters"] = len(extracted_text.strip())
            expected_checks = {
                expected: text_contains(extracted_text, expected) for expected in args.expected_text
            }
            report["pdf"]["expected_text"] = expected_checks
            if code != 0 or not extracted_text.strip():
                errors.append("PDF text extraction failed or produced an empty text layer")
            missing_expected = [text for text, found in expected_checks.items() if not found]
            if missing_expected:
                errors.append(f"Expected text missing from PDF text layer: {missing_expected}")
            if tool_output.strip():
                report["pdf"]["pdftotext_output"] = tool_output.strip()
        else:
            message = "pdftotext not found; searchable text was not checked"
            (errors if args.strict else warnings).append(message)

        pdffonts_path = executables.get("pdffonts")
        if pdffonts_path:
            command = [str(pdffonts_path), str(generated_pdf)]
            commands.append(command)
            code, fonts_output = run_command(command, cwd=main_tex.parent, env=env, timeout=60)
            fonts = parse_fonts(fonts_output)
            report["pdf"]["pdffonts_exit_code"] = code
            report["pdf"]["fonts"] = fonts
            report["pdf"]["all_fonts_embedded"] = bool(fonts) and all(
                font["embedded"] == "yes" for font in fonts
            )
            report["pdf"]["all_fonts_unicode_mapped"] = bool(fonts) and all(
                font["unicode"] == "yes" for font in fonts
            )
            if code != 0 or not fonts:
                errors.append("pdffonts could not enumerate fonts")
            elif not report["pdf"]["all_fonts_embedded"]:
                errors.append("One or more PDF fonts are not embedded")
            if fonts and not report["pdf"]["all_fonts_unicode_mapped"]:
                warnings.append("One or more fonts report uni=no; review actual text extraction")
        else:
            message = "pdffonts not found; font embedding was not checked"
            (errors if args.strict else warnings).append(message)

        if render_dir:
            pdftoppm_path = executables.get("pdftoppm")
            if pdftoppm_path:
                render_dir.mkdir(parents=True, exist_ok=True)
                prefix = render_dir / "page"
                command = [
                    str(pdftoppm_path),
                    "-png",
                    "-r",
                    str(args.render_dpi),
                    str(generated_pdf),
                    str(prefix),
                ]
                commands.append(command)
                code, render_output = run_command(command, cwd=main_tex.parent, env=env, timeout=args.timeout)
                rendered = sorted(render_dir.glob("page-*.png"))
                report["pdf"]["render_exit_code"] = code
                report["pdf"]["rendered_pages"] = [str(path) for path in rendered]
                page_count = report["pdf"].get("pages", 0)
                if code != 0:
                    errors.append(f"pdftoppm failed: {render_output.strip()}")
                if page_count and len(rendered) != page_count:
                    errors.append(
                        f"Rendered PNG count {len(rendered)} does not match PDF page count {page_count}"
                    )
            else:
                message = "pdftoppm not found; pages were not rendered"
                (errors if args.strict else warnings).append(message)

    report["pdf"]["published"] = False
    if not errors and candidate_sha256 is not None:
        try:
            copy_atomic(generated_pdf, output_pdf, candidate_sha256)
        except OSError as exc:
            errors.append(f"Final PDF publication failed: {exc}")
        else:
            report["pdf"]["sha256"] = candidate_sha256
            report["pdf"]["bytes"] = generated_pdf.stat().st_size
            report["pdf"]["published"] = True

    report["status"] = "success" if not errors else "failed"
    report["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    report["errors"] = errors
    report["warnings"] = warnings
    json_write(report_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
