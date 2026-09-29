---
name: research-paper-card
description: Deep-read one research paper into a traceable Claim-Evidence-Code card. Use when the user asks to understand, annotate, archive, compare, or add a paper to a research knowledge base, especially when claims must be tied to tables, equations, code, and limitations.
---

# Research Paper Card

Create a reusable research record rather than a prose summary.

## Source discipline

Use the paper itself as the primary source. Inspect appendices, supplementary material, official code, README, configuration, and evaluation scripts when available. Clearly mark anything inferred from abstracts, third-party summaries, or incomplete access.

Retain the exact paper version, access date, repository URL and commit when known. Never silently combine numbers from different versions.

## Reading sequence

1. Identify the problem, target setting, and non-goals.
2. Reconstruct the central claim and the mechanism claimed to cause it.
3. Extract observable predictions implied by that mechanism.
4. Map each important claim to evidence:
   - PDF page, section, equation, figure, or table;
   - dataset, split, metric, baseline, seeds, and compute;
   - code file, function, config, or command when available.
5. Record strongest supporting evidence and strongest counterevidence or missing control.
6. Inspect failure cases, limitations, and scope qualifiers.
7. Distinguish what is reported, what is implemented, and what was independently observed.

## Card schema

Use this structure:

```markdown
# Paper Card: <title>

## Identity
- Version / date / URL / code commit

## Problem and setting
- Problem:
- Scope and non-goals:

## Core contribution
- Claim:
- Mechanism:
- Observable prediction:

## Claim-Evidence-Code map
| ID | Claim | Paper evidence | Evaluation conditions | Code lever | Confidence |
|---|---|---|---|---|---|

## Results worth retaining
| Result | Value | Metric/split/budget | Exact source | Caveat |
|---|---:|---|---|---|

## Assumptions, failures, and missing controls

## Reproduction entry points
- Environment:
- Data:
- Train/eval commands:
- Missing artifacts:

## Transferable insight
- What may transfer:
- What appears setting-specific:
- Smallest decisive follow-up:
```

If writing to a project knowledge base, inspect its local conventions first. Avoid inventing a global `~/.paper-kb` location unless the user explicitly wants one.

## Quality gate

A card is incomplete if a headline number lacks metric/split/source, a contribution lacks a falsifiable prediction, or an asserted code lever was not found in the repository. Record `Unknown` instead of filling gaps from intuition.

## Lineage

Adapted from Dr. Pie 1.2.2 `kb-add`, with the storage convention generalized and Claim-Evidence-Code traceability strengthened.
