---
name: research-numbers-audit
description: Audit numeric claims in a Markdown or LaTeX research draft against JSON, CSV, or W&B summary result artifacts. Use after writing and before submission when the user asks to trace numbers, detect rounding drift, find unsupported deltas or significance, or produce a numeric provenance report.
---

# Research Numbers Audit

Treat this as a post-write provenance aid, not proof that the experiment, split, registry, or metric is correct.

Read [references/limitations.md](references/limitations.md) before interpreting the report.

## Preconditions

Identify the draft version and the authoritative result artifacts. Pin paths and, when possible, commit or content hashes. Do not mix development, held-out, old, and new result files without labeling them.

## Run the deterministic scan

Resolve the `scripts/` directory relative to this `SKILL.md`, then run:

```bash
python3 <skill-dir>/scripts/extract_numbers.py \
  --paper-dir <draft-dir> \
  --output <audit-dir>/extracted_numbers.json

python3 <skill-dir>/scripts/build_registry.py \
  --results-json <results.json> \
  --results-csv <optional-results.csv> \
  --wandb-summary <optional-wandb-summary.json> \
  --output <audit-dir>/number_registry.json

python3 <skill-dir>/scripts/verify.py \
  --extracted <audit-dir>/extracted_numbers.json \
  --registry <audit-dir>/number_registry.json \
  --output <audit-dir>/NUMBERS_AUDIT_REPORT.md
```

The result-file flags are repeatable. A non-zero verifier exit means blocking candidates were found; it does not prove fabrication.

## Manually validate identity

For each headline number, confirm semantic identity, not just value similarity:

- metric and unit;
- dataset, split, subset, and aggregation;
- method, baseline, checkpoint, and prompt/config;
- seed or confidence interval;
- budget and evaluator version;
- source artifact key and draft location.

Recompute deltas, relative improvements, averages, confidence intervals, and p-values from the pinned raw data when possible. Do not whitelist headline metrics merely to make the gate pass.

## Deliverable

Return the report plus a manually checked ledger with status `verified`, `candidate match`, `unresolved`, or `incorrect`. State what the scan cannot establish and which source-of-truth checks remain.

## Lineage

Adapted from Dr. Pie 1.2.2 `numbers-grounding`. The original scripts are retained locally with Markdown extraction fixes; interpretation is narrowed because value-only matching cannot establish semantic provenance.
