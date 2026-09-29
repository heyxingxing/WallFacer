# Portable runner contracts

No specific runtime, vendor API, corporate service, or CLI is required by this document. The selected runner must implement the following contract; until verified, its capabilities remain unconfirmed.

## Prepare

Create an isolated run workspace and immutable request containing run ID, logical comparison slot, parent/candidate identity, skill-resource hash, case hash, prompt, runtime/model configuration, evaluator version, budget, and expected artifacts. Record how the runtime will load the selected skill.

Preparation is local bookkeeping. It does not establish execution or authorize authentication, external changes, installation, or publication.

## Execute and collect

1. Verify the prepared hashes before launching the authorized runtime.
2. Record observed runtime identity, start/end times, terminal status, and resource usage where available.
3. Collect the complete available trajectory and generated artifacts through a trusted controller, not only a candidate-authored receipt.
4. Verify the relationship between request, runtime session, loaded skill, case, output, and evaluator input. Skill identity may be established by a runtime loader record with a content hash or a genuine tool read of the exact frozen file. A prompt mention is insufficient.
5. For claims that a tool action occurred, match a real call with its result and requested target. A fabricated tool name in prose or a local success flag is insufficient.
6. Reject malformed/partial traces, path escapes, unexpected symbolic links, hash drift, artifact collisions, and mismatched bindings. Preserve enough sanitized metadata to diagnose the rejection.

Do not persist credentials, authentication configuration, or unnecessary raw sensitive inputs in an experiment archive. Redaction must preserve a useful account of what was checked and what could not be retained.

## Failure classes

Distinguish skill behavior, runtime/collector, infrastructure, authentication/permission, missing data, and evaluator failures. Only attribute a failure to the skill when the collected evidence supports that causal claim. Treat external failures as inconclusive for skill improvement; report their frequency separately as an operational measure.

An LLM can help inspect evidence but cannot replace runtime provenance with confidence or self-report.

## Manual execution

When automation is unavailable, use the same frozen request and collect actual runtime artifacts manually. Record the operator, runtime, model, session ID where available, and timestamps. If skill identity or action provenance cannot be established, label that limitation rather than asserting verification.
