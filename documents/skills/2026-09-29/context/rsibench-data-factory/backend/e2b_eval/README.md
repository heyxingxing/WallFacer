# E2B Harbor Eval (cloud-only)

Run a fixed Harbor benchmark eval with **no local Docker and no local proxy**.
The benchmark task runs in an E2B sandbox; a small Tinker proxy runs in its own
E2B sandbox. The tinker API key never enters the task sandbox.

This is the eval path the runner uses: `run_chain.sh` and
`runner/run_official_eval.sh` call `python -m backend.e2b_eval`. The previous
local-Docker eval (local Harbor + local Tinker proxy) has been removed.

## Architecture

```
train:     tinker cloud
task env:  E2B task sandbox            (the测评环境 — untouched)
sampling:  proxy in its OWN E2B sandbox (get_host public URL, setsid-detached)
             ├─ parse output: Qwen <tool_call>  -> OpenAI tool_calls
             ├─ normalize input: OpenAI tool history -> Qwen text
             ├─ pin eval decoding params (max_tokens/temp/top_p/top_k)
             └─ route by default:
                  tinker:// checkpoints -> Tinker SDK SamplingClient
                  base model names       -> Tinker SDK SamplingClient
```

## Why a proxy is still needed

The proxy gives Harbor agents an OpenAI-compatible endpoint backed by Tinker.
For mini-swe-agent, it also fills the structured tool-call compatibility gap:
Qwen-style models emit `<tool_call>` text, and OpenAI tool history must be
rendered back into the Qwen chat format on the next turn. Terminus-2 can use the
same endpoint as plain chat-completions. The proxy also chooses the correct
Tinker backend:

- saved `tinker://.../sampler_weights/...` checkpoints use the Tinker SDK
  `SamplingClient`.
- base model names also use the Tinker SDK `SamplingClient`, because the
  OpenAI-compatible chat-completions shim does not cover every Tinker-supported
  base model or base-model LoRA checkpoint.

Putting it in a dedicated E2B sandbox keeps the task环境 untouched and avoids
exposing anything from your own machine.

## Verified end-to-end (实跑)

harbor 0.13.2, tinker 0.22.3, E2B Pro, against a real trained checkpoint:

- proxy sandbox reachable via `get_host` public URL; parses `<tool_call>` →
  `tool_calls` (verified from outside over the public URL)
- proxy survives the SDK connection closing (`setsid` detach) and the full eval
- task sandbox (E2B) reaches the proxy over the public URL; tinker key stays in
  the proxy sandbox only
- **matplotlib-14623 resolved, reward=1.0, 53-turn agent, 0 infra errors, ~6 min**

Evolution that got here (each step was a real, run-only finding):

| attempt | assistant turns |
|---|---|
| direct to tinker (no proxy) | 0 (no tool_calls) |
| proxy died after deploy (502) | 0 |
| proxy persistent, input not normalized | 1 (round 2 → 400) |
| proxy persistent + input normalize + output parse | **53 (full multi-turn)** |

## Usage

```python
from backend.e2b_eval.e2b_eval import run_e2b_eval

scores, proxy_url = await run_e2b_eval(
    model_path="tinker://.../sampler_weights/...",
    tinker_api_key=os.environ["TINKER_API_KEY"],   # E2B_API_KEY also required in env
    jobs_dir="artifacts/e2b_eval/<run>",
    harbor_dataset="swe-bench/swe-bench-verified",
    harbor_agent="mini-swe-agent",
    agent_config_profile="mini_swe_agent",
    n_tasks=100, n_concurrent=32,                   # official shape
    step_limit=200,
)
# scores: harbor_score / harbor-error diagnostics / tokens
```

Terminal-Bench 2.0 uses Harbor's Terminus-2 agent profile:

```python
scores, proxy_url = await run_e2b_eval(
    model_path="tinker://.../sampler_weights/...",
    tinker_api_key=os.environ["TINKER_API_KEY"],
    jobs_dir="artifacts/e2b_eval/tbench",
    harbor_dataset="terminal-bench/terminal-bench-2",
    harbor_agent="terminus-2",
    agent_config_profile="terminus_2",
    n_tasks=89, n_concurrent=32,
    step_limit=200,
)
```

GPQA Diamond also uses Harbor's Terminus-2 agent profile and the vendored local
Harbor dataset:

```python
scores, proxy_url = await run_e2b_eval(
    model_path="tinker://.../sampler_weights/...",
    tinker_api_key=os.environ["TINKER_API_KEY"],
    jobs_dir="artifacts/e2b_eval/gpqa",
    harbor_dataset="benchmarks/gpqa_diamond/datasets/seed23_random_100",
    harbor_agent="terminus-2",
    agent_config_profile="terminus_2",
    n_tasks=100, n_concurrent=32,
    step_limit=200,
)
```

AIME uses the same Terminus-2 profile with the vendored local Harbor dataset:

```python
scores, proxy_url = await run_e2b_eval(
    model_path="tinker://.../sampler_weights/...",
    tinker_api_key=os.environ["TINKER_API_KEY"],
    jobs_dir="artifacts/e2b_eval/aime",
    harbor_dataset="benchmarks/aime/datasets/full_30_2026",
    harbor_agent="terminus-2",
    agent_config_profile="terminus_2",
    n_tasks=30, n_concurrent=32, n_attempts=4,
    step_limit=200,
)
```

`run_e2b_eval` starts the proxy sandbox, runs the Harbor E2B job, reads the
Harbor score, and always tears the proxy sandbox down.

For base-model eval, pass the base model as `model_path`:

```python
scores, proxy_url = await run_e2b_eval(
    model_path="Qwen/Qwen3.6-35B-A3B",
    tinker_api_key=os.environ["TINKER_API_KEY"],
    jobs_dir="artifacts/e2b_eval/base",
)
```

The SDK-backed path automatically builds and reuses the fixed E2B template
`rsibench-data-tinker-proxy` from `proxy_template/Dockerfile`.

## Files

| File | Role |
|---|---|
| `tool_proxy.py` | hybrid proxy (runs in sandbox): parse tool_calls, normalize tool history, pin decoding, route to Tinker OAI or SDK backend |
| `e2b_proxy_manager.py` | proxy sandbox lifecycle: create, upload, detach-launch, get_host, keepalive, kill |
| `proxy_template.py` | fixed E2B template builder for SDK-backed proxy sandboxes |
| `proxy_template/Dockerfile` | preinstalls Tinker SDK/tokenizer dependencies in the proxy template |
| `e2b_eval.py` | build E2B JobConfig, run the job, read Harbor score (`run_e2b_eval`) |

## Known constraints / not yet done

- **Public proxy URL**: E2B `get_host` URLs are reachable by anyone with the URL
  (sandbox id is random). `run_e2b_eval` sets a per-run bearer key and
  `tool_proxy.py` enforces it.
- tinker's OpenAI endpoint is **beta / "low throughput"**; a full sustained
  100×32 run should still be watched on every backend/model.
- Validated at 1 task; the 100×32 path is the same code with default config.
- No HTTP service wrapper here yet (this is the core library + orchestration);
  the FastAPI shape from `backend/eval_service/` can be layered on later.
- E2B sandbox cost (proxy + task sandboxes) is outside the tinker budget.
