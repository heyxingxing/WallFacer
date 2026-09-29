---
name: research-reflection
description: Update research beliefs, priorities, and reusable knowledge after new papers, experiments, failures, or reviews. Use when the user asks to reflect, revise a research direction, summarize lessons from recent evidence, update a knowledge base, or decide what to stop, continue, or test next.
---

# Research Reflection

Make belief revision explicit. A reflection is not a celebratory summary and not a license to generalize beyond the evidence.

## Inputs

Collect the previous belief or plan, the new artifacts, and their evidence quality. Prefer raw results, logs, code diffs, paper passages, and reviewer findings over recollection.

## Reflection loop

For each material belief:

1. State the prior belief and why it was held.
2. State the new evidence and its scope.
3. List plausible alternative explanations.
4. Classify the update:
   - strengthened;
   - weakened;
   - narrowed to specific conditions;
   - overturned;
   - unchanged because evidence is not diagnostic.
5. Record the revised belief with confidence and boundary conditions.
6. Choose the next action with the highest expected information gain.

Do not treat one failed MVP as a global dead end until implementation, data, optimization, evaluation, and baseline validity have been checked. Do not treat one successful seed or development case as generalization evidence.

## Output

```markdown
# Research Reflection

## Evidence added
| Artifact | What it establishes | What it does not establish | Reliability |
|---|---|---|---|

## Belief updates
| Prior belief | New evidence | Alternative explanation | Updated belief | Confidence |
|---|---|---|---|---|

## Reusable patterns and dead ends

## Decisions
- Continue:
- Stop or park:
- Decisive next check:
- Stop condition:
```

Preserve negative and null results. A scoped `not evaluable` is better than a fabricated pass/fail judgment.

## Lineage

Adapted from Dr. Pie 1.2.2 `kb-reflect`, generalized from a fixed paper KB to any evidence-bearing research cycle.
