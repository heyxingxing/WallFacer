# Scheduling, retries, and stopping

## Plan

An experiment plan defines parent/candidates × cases × repetitions, budgets, evaluator identity, and required outputs. Give every comparison slot a stable ID and each concrete attempt a new run ID. Include matched parent slots rather than reusing an unrelated historical score.

Keep completed plans and records immutable. Updates create new versions with explicit ancestry. Track waiting for execution, collection, evaluation, review, complete, and terminal-failure states separately.

## Retry

Retry only under a declared policy, such as a transport failure before usable evidence was collected. A retry records its predecessor and reason, uses a new run ID, and preserves the failed attempt. Do not retry task failures selectively until the candidate looks better.

For each comparison slot, keep a single active attempt with an unambiguous replacement chain. Report retries and total cost, including failed attempts. Keep the parent and candidate retry policies comparable.

## Recovery

After interruption, verify hashes and terminal states before resuming. Continue an unfinished collection or review stage only if the saved evidence supports it. Never silently rerun a terminal attempt or overwrite a prior output.

Historical baseline evidence may be retained for context, but changing the evaluator, cases, tool access, or sampling policy requires a new matched comparison or an explicit non-comparability note.

## Budget and stopping

Choose limits appropriate to the task: money, tokens, wall time, runs, candidate count, and consecutive evaluable non-improvements. Stop when a hard limit is reached, the decisive question is answered, or further runs cannot resolve the present evidence gap.

Infrastructure-only outcomes do not count as evidence that a skill intervention failed, but their resource usage still counts against the budget.

## Outcome

Write improved or no-improvement only from a complete, comparable, current evidence set. Otherwise report inconclusive with the missing evidence. Pin the exact candidate, baseline, case set, evaluator, and result artifact hashes used in the decision.

An experiment outcome does not itself install a skill or publish a repository change.
