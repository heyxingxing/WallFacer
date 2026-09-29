# Numbers audit limitations

The bundled scripts are deterministic heuristics. Their output is a review queue, not an adjudication of research integrity.

## What the scan can do

- extract many numeric tokens from common LaTeX and Markdown draft layouts;
- flatten numeric values from JSON, CSV, and W&B summary exports;
- flag missing nearby values, out-of-tolerance drift, suspicious p-values, and confidence intervals without corresponding registry keys;
- retain draft locations and candidate result keys for manual review.

## What it cannot establish

- semantic identity between a draft number and a result value;
- correctness of the registry, experiment, split, method, metric, or evaluator;
- whether a value came from development, held-out, or cherry-picked runs;
- whether a reported delta, average, interval, or p-value was computed correctly unless recomputed from raw samples;
- completeness for arbitrary prose, tables generated through macros, figures, PDFs, notebooks, or custom file layouts.

The verifier searches globally for numerically similar values. Repeated values such as `0`, `1`, `50`, or common percentages can create false candidate matches. Manually verify metric, method, split, seed, unit, aggregation, and artifact key.

## Safe interpretation

Use four statuses:

- `verified`: semantic identity was manually confirmed or deterministically recomputed;
- `candidate match`: a value-only match exists but identity is unconfirmed;
- `unresolved`: no adequate source was found or required artifact is missing;
- `incorrect`: the draft value conflicts with the pinned source.

Do not use a whitelist to hide headline metrics. Whitelist only non-experimental constants such as years or dataset sizes, with a written rationale.
