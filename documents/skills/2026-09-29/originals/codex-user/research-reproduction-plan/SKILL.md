---
name: research-reproduction-plan
description: Convert a paper and its public artifacts into a staged, evidence-traceable reproduction plan. Use when the user asks to reproduce a paper, audit reproducibility, map claims to code, prepare a baseline rerun, or determine what can and cannot be reproduced from a PDF, README, repository, dataset, checkpoint, and evaluation protocol.
---

# Research Reproduction Plan

Plan reproduction before proposing improvements. A paper result, repository smoke test, and faithful paper-level reproduction are different evidence levels.

Read [references/output-contract.md](references/output-contract.md) when producing the full saved plan.

## Artifact audit

Inventory and pin:

- paper version and supplementary material;
- official repository and commit;
- environment and dependency files;
- data, preprocessing, splits, and licenses;
- checkpoints and model identifiers;
- train and evaluation entry points;
- reported commands, seeds, hardware, budgets, and statistical protocol;
- missing, inaccessible, ambiguous, or contradictory artifacts.

Do not infer availability from a paper link. Verify that each required artifact can actually be read or obtained in the authorized environment.

## Claim-Evidence-Code map

For every headline and supporting claim, record:

- exact paper evidence: page, table, figure, equation, or appendix;
- evaluation conditions: dataset, split, metric, baseline, budget, seeds;
- code lever: file, function, config, checkpoint, or command;
- reproduction level currently possible;
- unresolved ambiguity and decisive check.

If a claimed code lever is absent, say `not found`; do not invent a likely path.

## Freeze acceptance before execution

Specify primary metric, supporting metrics, split, baseline, allowed variance, hard guards, soft guards, compute budget, seed count, statistical treatment, artifact completeness, and failure conditions. Every threshold must have a source or an explicit user-approved engineering rationale.

## Stage the plan

Use increasing evidence levels:

1. `R0 artifact audit`: sources and missing pieces only.
2. `R1 interface validation`: environment resolves, entry points and schemas inspect successfully.
3. `R2 smoke`: tiny or synthetic run proves the pipeline, not the paper claim.
4. `R3 partial reproduction`: bounded subset with explicit deviations.
5. `R4 protocol reproduction`: aligned data, metric, budget, seeds, and reporting.

For each stage include commands, expected artifacts, pass/fail criteria, estimated cost, rollback, and stop condition. Do not let optimization contaminate the baseline reproduction branch.

## Handoff

End with: what is currently reproducible, what is blocked, the next decisive check, and which claims each completed stage would and would not establish.

## Lineage

Adapted from Dr. Pie 1.2.2 `paper-to-plan` and the acceptance-contract pattern in `autosota-replicate`. Removed AutoSOTA naming, Friday MCP, answer-leak checks tied to one benchmark, and assumptions about remote execution.
