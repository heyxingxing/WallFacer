---
name: research-critical-review
description: Perform an evidence-linked adversarial review of a research idea, plan, implementation, result, or draft. Use when the user asks for critical review, reviewer-style feedback, a red-team pass, a claim audit, minimal supplementary experiments, or a review-fix-review loop.
---

# Research Critical Review

Review artifacts, not the author's confidence. A self-critique is not an independent review; label it accurately. Use a fresh reviewer or separate agent only when available and authorized.

If the user asks only for review, do not edit artifacts. If they request improvements, close findings in severity order and then re-review affected claims.

## Establish the review contract

Identify artifact versions, claimed contribution, target venue or success standard, review scope, excluded areas, and evidence available. State when source code, raw results, data, or appendices are missing.

## Review dimensions

Check:

- problem importance and scope;
- novelty relative to primary sources;
- mechanism coherence and falsifiable predictions;
- Claim-Evidence-Code alignment;
- baseline fairness and evaluation comparability;
- ablations, alternatives, failure cases, and statistical support;
- reproducibility, artifact completeness, and provenance;
- safety, ethics, leakage, and unintended shortcuts;
- whether conclusions stay within observed conditions.

## Finding schema

Every material finding must include:

- stable fingerprint derived from artifact path/section and issue type;
- severity: `critical`, `major`, `minor`, or `question`;
- confidence: high, medium, or low;
- exact artifact location and evidence;
- claim at risk;
- why it matters;
- smallest decisive fix or experiment;
- estimated cost and what outcome would close the finding.

Do not issue a high-confidence finding without a specific artifact or source. Merge duplicates across rounds by fingerprint.

## Response and re-review

For each finding choose: accept, partially accept, reject with evidence, or defer. Update the Claims Matrix and TODO ordered by scientific risk and information gain. Close a finding only when the cited artifact or result changed and was read back. New findings remain distinct from reopened findings.

End with a bounded verdict: ready for the stated next stage, conditionally ready, not ready, or not evaluable. Reviewer scores alone do not prove correctness.

## Lineage

Adapted from Dr. Pie 1.2.2 `research-review` and `auto-review-loop`. Replaced Friday-only MCP calls and automatic “review until pass” behavior with tool-agnostic artifact review and explicit closure evidence.
