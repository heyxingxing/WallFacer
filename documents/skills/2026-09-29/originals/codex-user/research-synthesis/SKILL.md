---
name: research-synthesis
description: Synthesize a set of papers or research cards into method families, evidence patterns, disagreements, and actionable gaps. Use when the user asks for a topic synthesis, cross-paper comparison, research landscape, method taxonomy, or gap analysis from an existing corpus.
---

# Research Synthesis

Synthesize relationships across sources. Do not write one paragraph per paper.

## Preconditions

Establish the corpus, version, and selection bias. If the input set is too narrow to support a field-level claim, limit the conclusion to the provided corpus. Deduplicate paper versions and keep source identifiers.

## Workflow

1. Normalize each source into: problem, assumptions, mechanism, evaluation protocol, main result, limitations, and evidence strength.
2. Group by mechanism or causal idea, not by superficial vocabulary.
3. Reconstruct lineage: what each family inherits, changes, or rejects.
4. Align comparisons. Separate results with different datasets, splits, metrics, budgets, backbones, or access to privileged data.
5. Search for disagreement types:
   - contradictory empirical results;
   - different problem definitions;
   - hidden evaluation or resource mismatch;
   - untested mechanism claims;
   - negative or missing evidence.
6. Identify gaps that are both important and falsifiable. A gap is not merely “few papers exist.”
7. End with decision-relevant next work: decisive reading, reproduction, ablation, dataset check, or hypothesis test.

## Output

Include:

- corpus and scope statement;
- method-family table: family, mechanism, assumptions, representative sources, evidence, known failure;
- evaluation comparability matrix;
- consensus, disputes, and unresolved unknowns;
- gap candidates with importance, tractability, novelty risk, and falsification test;
- a short research agenda ordered by information gain.

Every field-level conclusion should cite multiple independent sources or be labeled as a bounded synthesis. Do not average incomparable benchmark numbers.

## Lineage

Adapted from Dr. Pie 1.2.2 `kb-synthesize`; removed the fixed `~/.paper-kb` storage contract and added explicit evaluation-alignment gates.
