# Reproduction plan output contract

Create a saved Markdown plan when the user requests an artifact. Use the project naming convention when one exists; otherwise use `REPRODUCTION_PLAN.md` in the user-approved target directory.

## Required sections

1. Research question and reproduction target
2. Source and artifact ledger
3. Claim-Evidence-Code matrix
4. Protocol alignment table
5. Missing artifacts and blockers
6. Frozen acceptance criteria
7. Staged plan R0-R4
8. Commands, outputs, estimates, and rollback
9. Risk and contamination controls
10. Conclusions each stage can and cannot support

## Source and artifact ledger

For every artifact record: role, exact version or commit, location, access date, integrity hash when practical, license or access constraint, and status (`verified`, `missing`, `ambiguous`, `inaccessible`).

## Protocol alignment table

Compare paper versus planned reproduction for data, preprocessing, split, model/checkpoint, metric implementation, decoding, seed count, budget, hardware-sensitive settings, and statistics. Mark each as exact, bounded deviation, unknown, or blocked.

## Acceptance criteria

Include:

- primary metric and direction;
- expected baseline and allowed variance with source;
- hard guards that invalidate the run;
- soft guards that reduce confidence;
- required seeds and statistical summary;
- resource ceiling;
- artifact completeness requirements;
- fail, partial, and success verdict rules.

Unknown gate inputs yield `pending` or `not evaluable`, never automatic pass.

## Reproducibility record

Require run ID, code commit and diff, command, config, data/model versions, environment snapshot, seed, timestamps, logs, raw outputs, and evaluation report. Preserve failed attempts and deviations.
