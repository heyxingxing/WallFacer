# Tinker Train And Eval

RSIBench-Data now uses Tinker for both training and model sampling.

The fixed chain is:

```text
train_messages.jsonl
  -> backend/tinker/train_lora_sft.py
  -> tinker://.../sampler_weights/... checkpoint
  -> python -m backend.e2b_eval
       (tool-call proxy sandbox + Tinker backend + Harbor on E2B)
```

## Training Data

Each line in `train_messages.jsonl` is:

```json
{
  "messages": [
    {"role": "system", "content": "You are an expert SWE agent."},
    {"role": "user", "content": "Fix the bug..."},
    {"role": "assistant", "content": "I will reproduce...", "loss": true}
  ]
}
```

Assistant messages are trainable by default. Set `"loss": false` to keep an
assistant message as context only.

The training wrapper renders Qwen chat templates, appends the selected
assistant response, then sends Tinker `Datum` records in the standard
right-shifted input / left-shifted target layout. Cross-entropy weights are
`0.0` on prompt positions and `1.0` on assistant response positions.

## Training

```bash
python3 backend/tinker/train_lora_sft.py \
  --run-id demo \
  --model Qwen/Qwen3.5-35B-A3B-Base \
  --train-data attempts/a1/train_messages.jsonl \
  --output artifacts/runs/demo/tinker_train_metadata.json \
  --max-steps 1 \
  --lora-rank 8
```

The output metadata contains `model_path`, a persistent Tinker sampler
checkpoint path suitable for `create_sampling_client(model_path=...)`.

## Eval (E2B)

```bash
set -a; source .env; set +a   # TINKER_API_KEY + E2B_API_KEY
python3 -m backend.e2b_eval \
  --model-path 'tinker://.../sampler_weights/...' \
  --run-dir artifacts/runs/<run_id> \
  --base-model Qwen/Qwen3.5-35B-A3B-Base \
  --n-tasks 100 --n-concurrent 32
```

This starts a tool-call proxy sandbox (it parses Qwen `<tool_call>` into OpenAI
`tool_calls` and normalizes tool history), runs Harbor SWE-bench Verified on E2B
task sandboxes, and writes `harbor/jobs/*/result.json` plus
`tinker_cost_estimate.json` under the run dir. Saved `tinker://` checkpoints and
base model names passed as `--model-path` use the Tinker SDK `SamplingClient` by
default; the first SDK-backed run automatically builds the fixed E2B template
`rsibench-data-tinker-proxy`, and later runs reuse it.

Base-model direct eval:

```bash
set -a; source .env; set +a
python3 -m backend.e2b_eval \
  --model-path Qwen/Qwen3.6-35B-A3B \
  --run-dir artifacts/runs/<run_id>-base \
  --base-model Qwen/Qwen3.6-35B-A3B \
  --n-tasks 50 --n-concurrent 32
```

The same fixed sampling settings apply to every attempt eval and runner final
eval (pinned by the proxy):

```text
max_tokens=4096
temperature=1.0
top_p=0.95
top_k=20
max_context_tokens=65536
max_prompt_tokens=61439
```

Do not use 128K/200K/256K context; the runner and validator cap context at 64K.
The fixed max prompt budget leaves one token of headroom:
`61439 = 65536 - 4096 - 1`.
`n_concurrent` is the eval sampling concurrency (Harbor's parallel requests).

## Cost Estimate

### Chat format and context integrity

Training and SDK inference share `backend/message_format.py`. Tool-call JSONL
records must include a top-level `tools` array with the exact evaluation function
schema. The lightweight mini-swe profile supplies `tools.json` from mini-swe-agent
2.4.5. Templates supply thinking boundaries and end-of-turn markers; do not append
a generic EOS to raw assistant text.

The trainer compares rendered **text** prefixes, then encodes the inference prefix
and its template-produced continuation separately. BPE can merge boundary
newlines, so separately tokenized full/prefix strings are not reliably prefix
aligned. A template failure or incompatible text prefix aborts training. The SDK
proxy also fails readiness if chat rendering fails; it cannot fall back to plain
role tags. Its Docker image explicitly installs `jinja2`, and template aliases
include the Dockerfile hash so changed dependencies create a new image.

Sampling always includes the template's end-of-turn stop: `<|im_end|>` for
Qwen3.5/3.6, following the official Tinker renderer. Caller stops may add to it
but cannot remove it. The parser stops at the first turn/role delimiter before
extracting tool calls, preventing invented later turns from becoming real
commands. Tool-call examples inside thinking are ignored, and nested/dangling
call blocks cannot be executed. Responses stopped by the output length limit retain `finish_reason=length`
and produce no executable tool calls, consistent with treating truncation as an
incomplete response. Raw sampling responses and stop reasons are preserved in the private
run's `tinker_proxy.log` for diagnosis; these logs may contain task/code text.

Use `train_max_length=65536` for Qwen3.5-35B-A3B-Base. This is a ceiling, not
padding. Both training and inference reject overlong sequences instead of silently
discarding system/task context. Rebuild an overlong sample explicitly, or select
a supported configuration. Do not raise this ceiling above the service limit.

The repair validation under `artifacts/runs/light-repair-20260920/` preserves the
original messages, adds only the evaluation tool schema, and verifies all 31
assistant targets plus exact local/E2B token parity before spending training
budget. The original experiment remains separate.

Before an attempt spends training budget, estimate scheduled training tokens:

```bash
python3 backend/tinker/estimate_attempt_cost.py \
  --model Qwen/Qwen3.5-35B-A3B-Base \
  --train-data attempts/a1/train_messages.jsonl \
  --run-config attempts/a1/run_config.json \
  --output attempts/a1/tinker_preflight_estimate.json
```

`run_attempt.sh` runs this estimator automatically. It uses the same tokenizer and
chat rendering path as training, then applies:

```text
estimated_train_tokens =
  sum(right-shifted sequence tokens for examples scheduled in the same cyclic
  order as training)

estimated_train_usd =
  estimated_train_tokens / 1_000_000 * train_usd_per_1m_tokens
```

The proxy records sample-token estimates through:

```bash
TINKER_PROXY_USAGE_JSONL=...
TINKER_PROXY_USAGE_SUMMARY=...
```

Default sample rates are configurable:

```bash
TINKER_PROXY_PREFILL_USD_PER_1M=0.36
TINKER_PROXY_SAMPLE_USD_PER_1M=0.89
TINKER_TRAIN_USD_PER_1M_TOKENS=1.07
```

For `Qwen/Qwen3.5-35B-A3B-Base`, RSIBench-Data defaults to the public Tinker rates:
`$0.36/M` prefill, `$0.89/M` sample, and `$1.07/M` train. Override the env vars
above to pin a different accounting policy.

Training cost is estimated before training and recorded after training in
`tinker_train_metadata.json`. Eval sampling cost is not knowable before the eval
runs; `python -m backend.e2b_eval` computes it from Harbor's prompt/output token
totals and writes `tinker_cost_estimate.json`.
