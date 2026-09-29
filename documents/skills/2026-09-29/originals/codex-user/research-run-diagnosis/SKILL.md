---
name: research-run-diagnosis
description: Diagnose a research experiment result or failure through implementation, data, optimization, evaluation, and method-hypothesis layers. Use when a run crashes, underperforms, disagrees with a paper, shows no signal, produces suspicious gains, or needs a bounded post-experiment interpretation.
---

# Research Run Diagnosis

Find the earliest layer that can explain the observation. Do not rescue the hypothesis by silently changing metrics, baselines, exclusions, or acceptance thresholds.

If the user asked only for diagnosis, inspect and report; do not implement fixes.

## Preserve the run

Record run identifier, code commit and diff, model and dataset versions, environment, command, config, seed, hardware, timestamps, logs, checkpoints, metrics, and evaluation artifacts. Distinguish a missing artifact from a negative result.

## Diagnose in order

### 1. Implementation

Check entry point, config binding, shapes, masking, precision, device placement, checkpoint loading, gradients, unit tests, and whether the intended code path executed.

### 2. Data

Check version, split leakage, preprocessing parity, label or schema quality, sampling, truncation, contamination, and train/eval distribution.

### 3. Training or optimization

Check loss behavior, learning-rate schedule, batch and accumulation semantics, instability, saturation, compute equivalence, seed variance, and whether the baseline was calibrated first.

### 4. Evaluation

Check metric implementation, aggregation, normalization, prompt or decoding settings, evaluator version, significance calculation, missing cases, and whether the reported number is actually comparable.

### 5. Method hypothesis

Only after the earlier layers are credible, ask whether the mechanism is wrong, too weak, limited to another regime, or confounded by an alternative explanation.

## Competing hypotheses

Maintain a table of candidate causes, supporting evidence, contradicting evidence, confidence, and cheapest decisive test. Prefer tests that separate multiple explanations at once.

## Deliverable

Report:

- observed outcome and its verified scope;
- highest-confidence cause and remaining alternatives;
- layer-by-layer checks completed and missing;
- smallest decisive next test;
- whether rerun, rollback, parameter change, or method revision is justified;
- `INSIGHTS_FROM_RUN`: what transfers, what does not, and what remains unknown.

A failed process and a falsified method are different outcomes. A successful smoke test and an improved method are also different outcomes.

## Lineage

Adapted from the five-layer diagnosis embedded in Dr. Pie 1.2.2 `plan-to-experiment`, without remote SSH, HOPE scheduling, or missing sibling-script dependencies.
