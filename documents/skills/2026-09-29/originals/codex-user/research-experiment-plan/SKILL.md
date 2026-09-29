---
name: research-experiment-plan
description: Turn a refined research claim or method proposal into a claim-driven experiment roadmap with frozen evaluation and acceptance criteria. Use when the user asks for an experiment plan, ablation matrix, evaluation protocol, run order, compute budget, baseline design, or paper-ready validation.
---

# Research Experiment Plan

Design experiments to discriminate claims, not merely to generate tables. Do not run experiments unless the user also asks for execution.

Read [references/experiment-contract.md](references/experiment-contract.md) when writing the complete plan artifact.

## Freeze claims first

State:

- primary claim;
- supporting claims;
- anti-claim or credible alternative explanation;
- minimum evidence required for each;
- scope and conditions under which the claim is intended to hold.

If the method cannot produce an observable prediction different from the anti-claim, the experiment is not yet diagnostic.

## Lock evaluation

Before designing the main method run, freeze dataset version, split, metric implementation, baseline code and checkpoint, preprocessing, seed policy, budget, hardware-relevant constraints, and statistical treatment. Build or inspect the evaluation path before the training path.

## Experiment blocks

Choose only blocks needed by the claims:

- baseline calibration and reproducibility;
- main anchor comparison;
- novelty isolation through controlled ablation;
- simplicity or cost comparison;
- scaling or frontier-necessity test;
- robustness and distribution-shift checks;
- mechanism probes;
- failure and boundary analysis;
- held-out or independent confirmation.

For every experiment specify: claim tested, variable changed, controls held fixed, command or code lever, expected outcomes under claim and anti-claim, required artifact, destination figure/table, cost, and stop condition.

## Run ordering

Order by information gain per unit cost: evaluation unit tests → baseline lock → minimum falsification test → main comparison → essential ablations → robustness/scaling → expensive confirmation. Fail fast on invalid baselines or broken evaluation.

## Quality gates

- Headline results require aligned baselines and evaluation hygiene.
- One seed or development case is preliminary evidence.
- Unknown or missing gate signals cannot be silently treated as pass.
- Structural completion does not establish scientific validity.
- Acceptance rules may downgrade a verdict; they must not promote unsupported evidence.

## Lineage

Adapted from Dr. Pie 1.2.2 `experiment-plan`, `idea-to-plan`, and `autosota-replicate`; reduced prompt bulk and converted aspirational gates into explicit artifact and acceptance contracts.
