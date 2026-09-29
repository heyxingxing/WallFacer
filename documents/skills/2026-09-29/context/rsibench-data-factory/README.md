<h1 align="center">RSIBench-Data</h1>

<p align="center">
  <strong>Budget-aware synthetic data generation and post-training for long-horizon agent benchmarks.</strong>
</p>

<div align="center">

[![Website][website-image]][website-url]
[![Evolvent AI][evolvent-image]][evolvent-url]
[![X][x-image]][x-url]
[![LinkedIn][linkedin-image]][linkedin-url]
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Training: Tinker](https://img.shields.io/badge/Training-Tinker-111827)
![Evaluation: Harbor](https://img.shields.io/badge/Evaluation-Harbor-0F766E)
![Runtime: E2B](https://img.shields.io/badge/Runtime-E2B-F97316)
[![License][license-image]][license-url]

</div>

RSIBench-Data evaluates whether a data-generation agent can improve a target
model by synthesizing benchmark-specific post-training data under a fixed,
real training and evaluation chain. The agent is given a wall-clock budget and
a Tinker cost budget, then iteratively creates training data, launches LoRA SFT,
evaluates the resulting checkpoint, and selects a final submission.

## System Overview

<p align="center">
  <img src="assets/system_overview.png" alt="Tinker training and evaluation pipeline" width="100%">
</p>

Training and sampling run on Tinker. Evaluation runs entirely in E2B cloud
sandboxes through the proxy, so no local Docker runtime is required. The E2B
implementation lives in [`backend/e2b_eval/`](backend/e2b_eval/).

### Core Properties

- **Closed-loop data optimization**: generate data, train, evaluate, inspect,
  and iterate within explicit time and cost budgets.
- **Real post-training**: every attempt uses Tinker LoRA SFT and produces a
  sampler checkpoint used by the evaluation proxy.
- **Isolated cloud evaluation**: Harbor agents and task environments run in
  per-attempt E2B sandboxes.
- **Multiple orchestrator harnesses**: the same workspace contract supports
  Claude Code, Codex, and Kimi Code.
- **Benchmark-specific profiles**: each profile fixes the prompt, dataset,
  Harbor agent, evaluation shape, and allowed seed factories.
- **Auditable artifacts**: training inputs, estimates, model usage, Harbor
  trajectories, verifier outputs, and final-selection records are retained.

## Benchmark Profiles

`TARGET_BENCHMARK` is resolved through `benchmarks/*/spec.json`. Each profile
defines its own data-agent prompt, Harbor configuration, official evaluation
shape, and seed-factory allowlist.

| `TARGET_BENCHMARK` | Official dataset | Harbor agent | Tasks | Attempts | Seed factories |
|---|---|---:|---:|---:|---|
| `swe-bench-verified` | Local seed-23 random SWE-bench Verified subset | `mini-swe-agent` | 100 | 1 | SWE-smith, SWE-Gym, swe-factory |
| `swe-bench-multilingual` | Local seed-23 random SWE-bench Multilingual subset | `mini-swe-agent` | 100 | 1 | SWE-smith, SWE-Gym, swe-factory |
| `swe-bench-pro` | Local seed-23 random SWE-bench Pro subset | `mini-swe-agent` | 100 | 1 | SWE-smith, SWE-Gym, swe-factory |
| `terminal-bench-2` | `terminal-bench/terminal-bench-2` | `terminus-2` | 89 | 1 | endless-terminals, tmax |
| `gpqa-diamond` | Local seed-23 random GPQA Diamond subset | `terminus-2` | 100 | 1 | synthetic-data-kit |
| `aime` | Full 30-task MathArena AIME 2026 dataset | `terminus-2` | 30 | 4 | synthetic-data-kit |

If `TARGET_BENCHMARK` is omitted, `swe-bench-verified` is used.

### Evaluation Data Boundary

`benchmarks/swe_bench_verified/runs/qwen35base_seed23_random100/` is read-only
diagnostic context for the data-generation agent. It contains the raw
Qwen3.5-35B-A3B-Base 100-task Harbor run, including per-task results,
mini-swe-agent trajectories, verifier reports, and Tinker usage and cost logs.

Agents may inspect these artifacts to understand benchmark distribution,
failure modes, and runtime constraints. They must not copy, transform, filter,
distill, or otherwise derive training records from benchmark tasks or
artifacts. Training data must be newly synthesized from non-benchmark public
sources, rather than invented without source grounding. Because this base run
uses the same official SWE-bench Verified subset used for evaluation, every
file under the directory must be treated as an evaluation-set artifact.

## Quick Start

### 1. Install Runtime Prerequisites

- Python 3.12
- A Tinker API key with access to `Qwen/Qwen3.5-35B-A3B-Base`
- An E2B API key; the Pro plan is recommended for evaluation workloads
- Claude Code CLI as `claude` when `DATA_AGENT_HARNESS=claude-code`
- Codex CLI as `codex` when `DATA_AGENT_HARNESS=codex`
- Kimi Code CLI as `kimi` when `DATA_AGENT_HARNESS=kimi-code`

Install Claude Code with Anthropic's native installer on macOS, Linux, or WSL:

```bash
curl -fsSL https://claude.ai/install.sh | bash
claude --version
```

Alternative official package-manager installs:

```bash
# macOS
brew install --cask claude-code

# Windows
winget install Anthropic.ClaudeCode
```

Install Codex in a Node/npm environment:

```bash
npm install -g @openai/codex
codex --version
```

Install Kimi Code with Moonshot's installer, or with npm on Node.js 22.19.0 or
newer:

```bash
curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash
kimi --version
```

For interactive local Claude Code use, run `claude` once and complete its login
flow. Automated RSIBench-Data sessions can instead use repository-local `.env`
API configuration, described below.

### 2. Create the Python Environment

```bash
bash tools/setup_env.sh
source .venv/bin/activate
```

### 3. Initialize Seed Factories

Seed factories are read-only references used by the data-generation agent. The
selected benchmark profile exposes only the factories in its allowlist; a
custom profile can opt into all factories with `"seed_factories": ["*"]`.

```bash
git submodule update --init --recursive seed_factories
```

The agent must inspect the exposed references when designing training data.

### 4. Configure Secrets and Models

```bash
cp .env.example .env
```

Required fields:

```dotenv
TINKER_API_KEY=...
E2B_API_KEY=...
```

The model names and API-version strings below are **example values**, not a
compatibility guarantee. Providers and account entitlements change over time:
before starting a paid run, replace them with values supported by your current
Tinker, Anthropic, and Codex-compatible endpoint accounts. The repository
defaults `TARGET_MODEL` to `Qwen/Qwen3.5-35B-A3B-Base`; the documented session
and base-model examples use that same model for consistency. Other
Tinker-supported target models (for example a Qwen 3.6 variant, when available
to your account) may be supplied explicitly as `TARGET_MODEL`.

Common optional fields:

```dotenv
# Claude Code harness only
ANTHROPIC_BASE_URL=...
ANTHROPIC_API_KEY=...
ANTHROPIC_AUTH_TOKEN=
ANTHROPIC_MODEL=claude-opus-4-8
ANTHROPIC_DEFAULT_OPUS_MODEL=
ANTHROPIC_DEFAULT_SONNET_MODEL=
ANTHROPIC_DEFAULT_HAIKU_MODEL=
ANTHROPIC_DEFAULT_FABLE_MODEL=
CLAUDE_CODE_SUBAGENT_MODEL=
ENABLE_TOOL_SEARCH=
CLAUDE_CODE_AUTO_COMPACT_WINDOW=
CLAUDE_CODE_EFFORT_LEVEL=
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=

# Codex harness only
CODEX_BASE_URL=...
CODEX_API_KEY=...
CODEX_MODEL=gpt-5.5
CODEX_RESPONSES_API_VERSION=2025-04-01-preview

# Generated rollout/API calls made by data-generation scripts
DATA_AGENT_ROLL_BASE_URL=...
DATA_AGENT_ROLL_API_KEY=...
DATA_AGENT_ROLL_MODEL=claude-opus-4-8
```

The Claude Code harness uses `ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL`, and either
`ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN`. `ANTHROPIC_MODEL` is also the
default `DATA_AGENT_MODEL` for the Claude Code orchestrator. Additional Claude
Code environment variables can be set in `.env` and are passed through to the
Claude subprocess.

Generated data scripts that perform rollout/API calls use
`DATA_AGENT_ROLL_BASE_URL`, `DATA_AGENT_ROLL_API_KEY`, and
`DATA_AGENT_ROLL_MODEL`.

When `DATA_AGENT_HARNESS=claude-code`, the runner passes the configured Claude
Code environment to the Claude subprocess. `ANTHROPIC_API_KEY` mode uses Claude
Code's bare/project setting path; `ANTHROPIC_AUTH_TOKEN` mode is used as-is.
Both credential fields may be left unset to use the caller's existing Claude CLI
configuration.

The Codex harness uses `CODEX_BASE_URL`, `CODEX_API_KEY`, and `CODEX_MODEL`.
It creates a session-local `CODEX_HOME` and a custom model provider backed by
the configured endpoint, so it does not depend on machine-level Codex login
state. Codex sessions require both `CODEX_BASE_URL` and `CODEX_API_KEY`.

The Kimi Code harness uses `KIMI_MODEL_NAME`, `KIMI_MODEL_API_KEY`, and optional
`KIMI_MODEL_BASE_URL`. It creates a session-local `KIMI_CODE_HOME` with only the
required permission setting, so it does not depend on machine-level Kimi login
state. Kimi Code sessions use `default_permission_mode = "yolo"`.

Runner scripts load `.env` in override mode. Repository-local values therefore
take precedence over same-named variables in the caller's shell.

### Optional Docker Isolation

The standard entrypoint still runs directly on the host:

```bash
bash runner/run_session.sh
```

To run the entire session inside Docker while mounting only this repository,
build the runtime image and use the Docker wrapper:

```bash
docker build --network=host \
  --build-arg CLAUDE_CODE_VERSION=2.1.197 \
  --build-arg CODEX_CLI_VERSION=0.142.5 \
  --build-arg HTTP_PROXY=http://127.0.0.1:7890 \
  --build-arg HTTPS_PROXY=http://127.0.0.1:7890 \
  -f docker/rsibench-runtime.Dockerfile \
  -t rsibench-runtime:ubuntu24-claude-2.1.197-codex-0.142.5 \
  docker

bash tools/run_session_in_docker.sh
```

The wrapper mounts `/data/RSIBench-Data` to the same path inside the container,
loads `.env`, and then runs `bash runner/run_session.sh` in the container. This
keeps the runner, data-agent CLI, Tinker calls, and official eval in one
container view while preventing access to host directories that are not mounted,
such as external archive folders. It also hides the repo-local
`archived_artifacts/` directory with a container-only tmpfs mount, then archives
the completed `RUN_ID` from `artifacts/runs/` into that host directory after the
container exits. Keep `artifacts/` fresh before starting a new isolated run if
old active run records should not be visible to the data agent.

The image includes Claude Code `2.1.197` and Codex CLI `0.142.5` by default and
reuses the repository `.venv` through the mount, so the container should use an
Ubuntu 24.04-compatible host `.venv`. Override `RSIBENCH_DOCKER_IMAGE` to use a
different runtime image.
Omit the proxy build args when the host does not expose a local proxy on port
`7890`.

### 5. Validate the Environment

```bash
bash tools/check_environment.sh
```

This check imports the real Tinker, E2B, and Harbor execution path and verifies
that `TINKER_API_KEY` and `E2B_API_KEY` are present. If it fails, rerun
`bash tools/setup_env.sh`, activate `.venv`, and check `.env`.

### 6. Run a One-Task Paid Smoke Test

Use this before a budgeted session to exercise the actual Tinker sampling, E2B
proxy, and Harbor path on one task. It does **not** test the Claude Code/Codex
orchestration loop, and it can incur Tinker and E2B charges.

```bash
set -a; source .env; set +a
python3 -m backend.e2b_eval \
  --model-path Qwen/Qwen3.5-35B-A3B-Base \
  --run-dir artifacts/runs/smoke-base-qwen35 \
  --base-model Qwen/Qwen3.5-35B-A3B-Base \
  --n-tasks 1 --n-concurrent 1
```

Success creates `artifacts/runs/smoke-base-qwen35/harbor/jobs/*/result.json`
and `tinker_cost_estimate.json`. Inspect the result before increasing
`--n-tasks` to 2 or 3 or starting a full session.

## Run an Experiment

The main entrypoint is [`runner/run_session.sh`](runner/run_session.sh).

### Claude Code

```bash
RUN_ID=qwen35base-claude-code-opus48-001 \
DATA_AGENT_HARNESS=claude-code \
TARGET_MODEL=Qwen/Qwen3.5-35B-A3B-Base \
TARGET_BENCHMARK=swe-bench-verified \
WALL_TIME_BUDGET_SEC=14400 \
TINKER_COST_BUDGET_USD=25 \
RUN_OFFICIAL_EVAL=1 \
bash runner/run_session.sh
```

### Claude Code with Kimi

For Kimi runs, put the Claude Code provider settings in `.env` and run the
Claude Code harness normally.

```dotenv
ANTHROPIC_BASE_URL=https://api.moonshot.cn/anthropic
ANTHROPIC_AUTH_TOKEN=<YOUR_MOONSHOT_API_KEY>
ANTHROPIC_MODEL=kimi-k3[1m]
ANTHROPIC_DEFAULT_OPUS_MODEL=kimi-k3[1m]
ANTHROPIC_DEFAULT_SONNET_MODEL=kimi-k3[1m]
ANTHROPIC_DEFAULT_HAIKU_MODEL=kimi-k3[1m]
ANTHROPIC_DEFAULT_FABLE_MODEL=kimi-k3[1m]
CLAUDE_CODE_SUBAGENT_MODEL=kimi-k3[1m]
ENABLE_TOOL_SEARCH=false
CLAUDE_CODE_AUTO_COMPACT_WINDOW=1048576
CLAUDE_CODE_EFFORT_LEVEL=max
```

```bash
RUN_ID=qwen35base-kimi-k3-claude-code-001 \
DATA_AGENT_HARNESS=claude-code \
TARGET_MODEL=Qwen/Qwen3.5-35B-A3B-Base \
TARGET_BENCHMARK=swe-bench-verified \
WALL_TIME_BUDGET_SEC=14400 \
TINKER_COST_BUDGET_USD=25 \
RUN_OFFICIAL_EVAL=1 \
bash runner/run_session.sh
```

### Codex

Claude Code and Codex receive the same generated workspace prompt and
instruction files. Codex-specific code changes only how that prompt is
executed.

```bash
RUN_ID=qwen35base-codex-gpt55-001 \
DATA_AGENT_HARNESS=codex \
TARGET_MODEL=Qwen/Qwen3.5-35B-A3B-Base \
TARGET_BENCHMARK=swe-bench-verified \
WALL_TIME_BUDGET_SEC=14400 \
TINKER_COST_BUDGET_USD=25 \
RUN_OFFICIAL_EVAL=1 \
bash runner/run_session.sh
```

### Kimi Code

```dotenv
KIMI_MODEL_NAME=kimi-k3[1m]
KIMI_MODEL_API_KEY=<YOUR_MOONSHOT_API_KEY>
# KIMI_MODEL_BASE_URL=https://api.moonshot.ai/v1
# KIMI_MODEL_THINKING_EFFORT=max
```

```bash
RUN_ID=qwen35base-kimi-code-k3-001 \
DATA_AGENT_HARNESS=kimi-code \
TARGET_MODEL=Qwen/Qwen3.5-35B-A3B-Base \
TARGET_BENCHMARK=swe-bench-verified \
WALL_TIME_BUDGET_SEC=14400 \
TINKER_COST_BUDGET_USD=25 \
RUN_OFFICIAL_EVAL=1 \
bash runner/run_session.sh
```

For Claude Code, `DATA_AGENT_MODEL` defaults to `ANTHROPIC_MODEL`. For Codex,
it defaults to `CODEX_MODEL`. For Kimi Code, it defaults to `KIMI_MODEL_NAME`.
Generated scripts must use the separate `DATA_AGENT_ROLL_BASE_URL`,
`DATA_AGENT_ROLL_API_KEY`, and `DATA_AGENT_ROLL_MODEL` values for direct
rollout/API calls.

### Confirm a Successful Session

With `RUN_OFFICIAL_EVAL=1`, a successful command exits with code 0 and prints
these key log lines (with run-specific paths):

```text
final_selection=.../agent_workspace/final_selection.json
running official eval for final selection
.../official_eval/official_eval.json
```

The required final artifacts are:

- `artifacts/runs/<RUN_ID>/agent_workspace/final_selection.json` — a completed
  attempt was selected.
- `artifacts/runs/<RUN_ID>/official_eval/official_eval.json` — its `status` is
  `"completed"` and `return_code` is `0`.
- `artifacts/runs/<RUN_ID>/official_eval/harbor/jobs/*/result.json` — the
  Harbor result used by the official evaluation.

For a concise status check, run:

```bash
python3 - <<'PY'
import json
from pathlib import Path

run_id = "replace-with-your-run-id"
root = Path("artifacts/runs") / run_id
for path in (
    root / "agent_workspace/final_selection.json",
    root / "official_eval/official_eval.json",
):
    print(path, json.loads(path.read_text()))
PY
```

`RUN_OFFICIAL_EVAL=0` intentionally skips the final evaluation, so a
`final_selection.json` alone means only that a checkpoint was selected; it is
not a completed official run.

### Additional Benchmark Preparation

The SWE-bench Multilingual profile uses a fixed local seed-23 random 100-task
subset generated from `SWE-bench/SWE-bench_Multilingual`:

```bash
python tools/create_swe_multilingual_local_dataset.py \
  --seed 23 \
  --n-tasks 100 \
  --output-dir benchmarks/swe_bench_multilingual/datasets/seed23_random_100 \
  --overwrite
```

Set `TARGET_BENCHMARK=swe-bench-multilingual` to use that subset.

For GPQA Diamond, set `TARGET_BENCHMARK=gpqa-diamond`. The profile uses
`benchmarks/gpqa_diamond/datasets/seed23_random_100` with `terminus-2` and
exposes Meta Llama's `seed_factories/synthetic-data-kit`.

For AIME, set `TARGET_BENCHMARK=aime`. The profile uses
`benchmarks/aime/datasets/full_30_2026` with `terminus-2`, evaluates each task
with four attempts, and also exposes `seed_factories/synthetic-data-kit`.

## Session Contract

The runner starts a PostTrainBench-style, non-interactive agent session.
`DATA_AGENT_REPROMPT=1` is enabled by default. If Claude Code exits before
calling `final_submit.sh <attempt_id>`, the runner invokes `claude --continue`
while wall time and Tinker budget remain. Set `DATA_AGENT_REPROMPT=0` only when
a single Claude Code turn is intentional.

The generated agent workspace exposes four commands:

```text
timer.sh
budget_status.sh
run_attempt.sh <attempt_id>
final_submit.sh <attempt_id>
```

- `timer.sh` reports the remaining wall-clock budget.
- `budget_status.sh` reports committed attempt cost plus the estimate for any
  active attempt.
- `run_attempt.sh` validates, trains, and evaluates one candidate dataset.
- `final_submit.sh` selects the checkpoint that official final evaluation will
  reuse.

### Attempt Inputs

Each attempt must contain:

```text
attempts/<attempt_id>/train_messages.jsonl
attempts/<attempt_id>/run_config.json   # optional
```

`train_messages.jsonl` is JSONL. Every line is a JSON object with a `messages`
list containing at least one user message and one trainable assistant message.
Assistant messages are trainable unless `"loss": false` is set.

Before real Tinker training starts, `run_attempt.sh` executes the same runtime
check as `tools/check_environment.sh`. Missing packages or API keys therefore
fail before training budget is spent. It then writes:

```text
attempts/<attempt_id>/tinker_preflight_estimate.json
```

The preflight file estimates scheduled training tokens and training cost from
`train_messages.jsonl` and `run_config.json`. Evaluation sampling cost is
measured during Harbor evaluation from actual prompt and output tokens.

### Run Configuration

Supported `run_config.json` keys:

```json
{
  "train_max_steps": 1,
  "train_max_length": 65536,
  "train_learning_rate": "1e-4",
  "train_batch_size": 1,
  "train_gradient_accumulation_steps": 1,
  "train_weight_decay": 0.0,
  "train_grad_clip_norm": 0.0,
  "train_lora_rank": 8,
  "train_seed": 0,
  "train_max_records": 0,
  "train_on_all_assistant": false,
  "tinker_proxy_max_context_tokens": 65536,
  "tinker_proxy_max_prompt_tokens": 61439,
  "tinker_proxy_max_tokens": 4096,
  "tinker_temperature": 1.0,
  "tinker_top_p": 0.95,
  "tinker_top_k": 20,
  "eval_step_limit": 200,
  "n_concurrent": 32,
  "n_tasks": 100,
  "eval_timeout_sec": 0
}
```

Unknown keys are rejected. Proxy context and decoding settings, along with the
evaluation step limit, are fixed to match official evaluation; the validator
rejects attempts that change those evaluation hyperparameters. The legacy key
`mini_swe_step_limit` remains accepted as an alias for older SWE runs.

Every attempt evaluates the same official setting. When final evaluation is
enabled, the runner reuses only the selected Tinker sampler checkpoint and
reruns that setting. Harbor task errors and timeouts are recorded as
`harbor_errors` and reflected in the score, but a scored Harbor result remains
a completed, submittable attempt. The agent must call
`final_submit.sh <attempt_id>` to select its final checkpoint.

### Process and Deadline Safety

Attempts must run in the foreground:

```bash
bash run_attempt.sh <attempt_id>
```

Do not launch attempts with `nohup`, `&`, `disown`, `setsid`, watcher scripts,
or task/waiter mechanisms. If a continuation finds an attempt already running,
it must wait for that process rather than launch a duplicate.

The agent must also protect final submission near the deadline:

1. Before starting a new attempt after a completed attempt exists, compare the
   remaining wall time with the last full attempt runtime plus a 30-minute
   submission buffer.
2. If the next attempt increases training steps, records, LoRA rank, or maximum
   length, assume it needs at least two hours unless a measurement shows
   otherwise.
3. During the final two hours, do not start a heavier or speculative attempt
   over a completed best attempt; submit the best completed attempt instead.
4. With less than one hour remaining, immediately run
   `final_submit.sh <best_attempt_id>` when any completed attempt exists.

The benchmark profile fixes the official evaluation shape. Attempts always use
the selected profile's `OFFICIAL_EVAL_N_TASKS`, `OFFICIAL_EVAL_N_CONCURRENT`,
and `OFFICIAL_EVAL_STEP_LIMIT`. SWE-bench Verified evaluates the first 100 tasks
in the configured Harbor dataset order by default; Terminal-Bench 2.0 evaluates
89 tasks. Official subsets and public base-run artifacts are analysis-only and
cannot be used as training-data sources.

## Evaluation Runtime

Each attempt creates and tears down its own E2B sandboxes: one tool-call proxy
sandbox and the per-task Harbor sandboxes. The proxy selects its Tinker backend
automatically:

- Saved `tinker://.../sampler_weights/...` checkpoints use the Tinker SDK
  `SamplingClient`.
- Base model names such as `Qwen/Qwen3.5-35B-A3B-Base` also use the Tinker SDK
  `SamplingClient`.

The proxy uses the Tinker SDK `SamplingClient` by default for both saved
`tinker://.../sampler_weights/...` checkpoints and base model names such as
`Qwen/Qwen3.5-35B-A3B-Base`. The first SDK-backed evaluation builds the fixed
E2B template `rsibench-data-tinker-proxy`; subsequent runs reuse it.

### Direct Checkpoint Evaluation

To evaluate a trained checkpoint outside a budgeted session:

```bash
set -a; source .env; set +a   # TINKER_API_KEY + E2B_API_KEY
python3 -m backend.e2b_eval \
  --model-path 'tinker://.../sampler_weights/...' \
  --run-dir artifacts/runs/manual-eval \
  --base-model Qwen/Qwen3.5-35B-A3B-Base \
  --harbor-dataset swe-bench/swe-bench-verified \
  --harbor-agent mini-swe-agent \
  --agent-config-profile mini_swe_agent \
  --n-tasks 100 --n-concurrent 32 --step-limit 200
```

Use the following substitutions for other profiles:

| Profile | Dataset | Agent | Additional arguments |
|---|---|---|---|
| Terminal-Bench 2.0 | `terminal-bench/terminal-bench-2` | `terminus-2` | `--agent-config-profile terminus_2 --n-tasks 89` |
| GPQA Diamond | `benchmarks/gpqa_diamond/datasets/seed23_random_100` | `terminus-2` | `--agent-config-profile terminus_2 --n-tasks 100` |
| AIME | `benchmarks/aime/datasets/full_30_2026` | `terminus-2` | `--agent-config-profile terminus_2 --n-tasks 30 --n-attempts 4` |

### Direct Base-Model Evaluation

Pass a supported base model name as `--model-path` to evaluate it directly:

```bash
set -a; source .env; set +a
python3 -m backend.e2b_eval \
  --model-path Qwen/Qwen3.5-35B-A3B-Base \
  --run-dir artifacts/runs/manual-base-eval \
  --base-model Qwen/Qwen3.5-35B-A3B-Base \
  --n-tasks 50 --n-concurrent 32
```

Direct evaluation starts the proxy sandbox, runs Harbor on E2B, and writes
`harbor/jobs/*/result.json` plus `tinker_cost_estimate.json` under the run
directory. Sampling rates default to `$0.36/M` prefill tokens and `$0.89/M`
sample tokens. Override them with `TINKER_PROXY_PREFILL_USD_PER_1M` and
`TINKER_PROXY_SAMPLE_USD_PER_1M`.

## Artifacts and Accounting

Session outputs are written under `artifacts/runs/<run_id>/`.

| Artifact | Purpose |
|---|---|
| `agent_initial.jsonl` | Initial Claude Code stdout and stream events |
| `agent_continue_<n>.jsonl` | Continuation stream events when reprompting is enabled |
| `agent_custom_command.log` | Output from custom harness commands |
| `data_agent_usage.json` | Orchestrator usage and reported rollout/API usage |
| `data_agent_api_usage.jsonl` | Per-response usage from generated rollout/API calls |
| `harbor/jobs/*/result.json` | Harbor task and aggregate evaluation results |
| Attempt Harbor trajectories | Evaluated agent behavior and verifier evidence |

Generated data scripts that perform rollout/API calls should use
`runner.lib.claude_usage_client.create_message`. The wrapper uses only the
`DATA_AGENT_ROLL_BASE_URL`, `DATA_AGENT_ROLL_API_KEY`, and
`DATA_AGENT_ROLL_MODEL` configuration and appends one record per response to
`$DATA_AGENT_API_USAGE_LOG`, including `model`, `input_tokens`,
`cache_creation_input_tokens`, `cache_read_input_tokens`, and `output_tokens`.
This usage is retained for experiment accounting and does not consume the
Tinker budget.

## Failure Recovery

- **E2B timeout or proxy failure:** retain the run directory and inspect the
  attempt's `harbor_errors` and Harbor `result.json`. Confirm the E2B key,
  account capacity, and transient service status, then run the one-task smoke
  test again. Do not treat an infrastructure error as a score or repeatedly
  spend budget on the same failure.
- **Tinker training failure:** inspect
  `artifacts/runs/<RUN_ID>/agent_workspace/attempts/<attempt_id>/tinker_preflight_estimate.json`
  and the matching `artifacts/runs/<RUN_ID>-<attempt_id>/` logs. Correct the
  dataset/configuration issue or account access, then create a new attempt;
  failed attempts cannot be selected by `final_submit.sh`.
- **Budget exhausted:** no further attempt can start. If a completed attempt
  was already selected, run `RUN_ID=<RUN_ID> bash runner/run_official_eval.sh`
  to retry only the final evaluation after fixing infrastructure access. If no
  `final_selection.json` exists, the session did not complete and needs a new
  budgeted run.
- **Claude Code or Codex exits early:** `DATA_AGENT_REPROMPT=1` (the default)
  automatically continues the harness while wall time and Tinker budget remain.
  If the runner exits without `final_selection.json`, inspect
  `agent_initial.jsonl`, `agent_continue_*.jsonl`, and `budget_status.sh`.
  Re-running with the same `RUN_ID` preserves accounting but does not pause its
  original wall-clock deadline; use it only while time remains.

## Development Checks

Run the shell and unit checks before pushing changes:

```bash
bash -n \
  runner/run_session.sh \
  runner/run_official_eval.sh \
  runner/workspace_template/pipeline/run_chain.sh \
  runner/workspace_template/pipeline/train.sh \
  tools/check_environment.sh \
  tools/setup_env.sh

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

## Repository Layout

```text
backend/e2b_eval/                    E2B proxy and Harbor evaluation runtime
backend/tinker/                      Tinker training, pricing, and cost estimates
benchmarks/                          Benchmark profiles, datasets, and context
docs/tinker_train_eval.md            Tinker training and evaluation runbook
docs/tinker_cookbook.md              Local Tinker API notes for data agents
runner/                              Budgeted session and official-eval entrypoints
runner/lib/                          Validation, accounting, budget, and audit helpers
runner/workspace_template/pipeline/  Fixed training and E2B evaluation chain
seed_factories/                      Read-only synthetic-data reference projects
skills/rsibench-data-factory/        Data-factory operating instructions
tests/                               Unit tests for runner and evaluation contracts
tools/                               Environment and dataset preparation utilities
```

For deeper implementation details, see
[`docs/tinker_train_eval.md`](docs/tinker_train_eval.md),
[`docs/tinker_cookbook.md`](docs/tinker_cookbook.md), and the
[`RSIBench-Data factory skill`](skills/rsibench-data-factory/SKILL.md).

[website-image]: https://img.shields.io/badge/Website-rsibench.co-0f141b
[website-url]: http://rsibench.co
[evolvent-image]: https://img.shields.io/badge/Evolvent_AI-evolvent.co-0f141b
[evolvent-url]: https://evolvent.co
[x-image]: https://img.shields.io/twitter/follow/Evolvent_AI?style=social
[x-url]: https://x.com/Evolvent_AI
[linkedin-image]: https://img.shields.io/badge/LinkedIn-Evolvent_AI-0A66C2?logo=linkedin&logoColor=white
[linkedin-url]: https://www.linkedin.com/company/evolvent-ai
[license-image]: https://img.shields.io/badge/License-CC_BY--NC_4.0-blue.svg
[license-url]: https://creativecommons.org/licenses/by-nc/4.0/
