# Claim-driven experiment contract

Use this contract for the saved `EXPERIMENT_PLAN.md` and optional `ACCEPTANCE_CRITERIA.md`.

## Experiment plan sections

1. Problem evidence, scope, and non-goals
2. Primary claim, supporting claims, and anti-claim
3. Mechanism and observable predictions
4. Frozen evaluation protocol
5. Baseline calibration
6. Experiment matrix
7. Run order and decision tree
8. Resource budget and scheduling assumptions
9. Artifact and provenance requirements
10. Failure interpretation and stop conditions

## Experiment row schema

| ID | Claim tested | Intervention | Fixed controls | Expected if claim | Expected if anti-claim | Artifact | Figure/table | Cost | Stop condition |
|---|---|---|---|---|---|---|---|---|---|

Every experiment must change one interpretable factor or explicitly model interactions. If a row cannot distinguish the claim from an alternative explanation, revise or remove it.

## Acceptance criteria

Freeze before running:

- metric code and direction;
- data/split version;
- baseline commit/config/checkpoint;
- min-pass threshold and source;
- ideal target and source or rationale;
- hard/soft guards;
- seed count and aggregation;
- significance or uncertainty policy;
- compute ceiling;
- required output files;
- fail, partial, pending, and success verdict rules.

Verdict rules are monotonic: missing evidence, guard failure, or held-out failure can downgrade but cannot promote a result.

## Decision tree

At each stage define:

- continue condition;
- cheapest diagnostic if ambiguous;
- stop or rollback condition;
- which later runs become unnecessary.

Do not schedule expensive scaling until evaluation and baseline calibration pass.
