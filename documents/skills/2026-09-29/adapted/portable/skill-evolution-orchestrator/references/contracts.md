# Evaluation and promotion contracts

## Cases and partitions

Give each case a stable identifier, input/source version, content hash, task constraints, and required artifacts. Record where any reference answer or gold label came from. Do not generate gold by rephrasing the same model output being evaluated.

Use disjoint feedback, validation, and final-test cases when the claim concerns generalization. Feedback cases and their traces may guide improvements. The selector may use validation scores, but the optimizer should not receive hidden case identities or answer details. Final-test results are only consulted after selecting and freezing a version.

If data only support a single-case pilot, label the result as a pilot. Do not manufacture partitions, independent labels, or sample counts to pass a readiness check.

## Matched comparison

Compare candidate and parent on the same case set, sampling policy, permitted tools, model configuration, evaluator version, and resource limits. Keep a per-case, per-repetition record. One baseline run cannot substitute for a full candidate matrix.

Report missing and failed cases rather than silently shrinking the denominator. State the number of repetitions and the limits of uncertainty estimates; one successful run is preliminary evidence.

## Proposal and candidate

Record:

- parent hash and relevant failure evidence;
- behavior-changing hypothesis and permitted files;
- expected change and credible alternative explanation;
- acceptance checks and possible regressions;
- intended scope: case-specific, domain-specific, or general.

Freeze the complete candidate after checking that the actual diff matches the declared intervention. Preserve scripts and references that affect behavior, not only SKILL.md.

## Evaluation

Run deterministic structural and task checks before subjective judging. Keep these distinct:

1. artifact integrity and runtime completion;
2. process conformance and tool-use evidence;
3. task outcome against an independent reference;
4. model or human qualitative review.

Only call a metric accuracy, precision, recall, or F1 when the reference standard, prediction mapping, and denominator justify it. Otherwise report named process metrics such as artifact completeness or required-check pass rate.

## Blind review

When comparing outputs blindly, omit candidate names, ancestry, proposal rationale, prior scores, and runtime metadata that reveals the condition. Bind each opaque review ID privately to the exact run and artifact hashes. Check both filenames and content for identity leakage.

Use pass, fail, uncertain, or tie with evidence locations. A qualitative review remains advisory and does not create independent gold.

## Selection and promotion

Compare quality, reliability, and cost under the frozen protocol. A Pareto comparison can expose tradeoffs without hiding them in an arbitrary aggregate score. Reject blocking invariant failures even if the average improves.

A promotion record identifies the selected hash, parent, comparison data, evaluator, independent-test status, known regressions, decision maker, and scope. Require a material supported benefit, no unacceptable critical regression, and authorization for the actual installation or publication. A favorable report alone does not change the active skill.
