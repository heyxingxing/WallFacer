# Tinker Cookbook Notes

This file is the local short reference for evaluated agents. Use it before
spending time rediscovering Tinker interfaces.

Official references:

- Tinker Cookbook GitHub: `https://github.com/thinking-machines-lab/tinker-cookbook`
- Tinker quickstart: `https://tinker-docs.thinkingmachines.ai/tinker/quickstart/`
- TrainingClient API: `https://tinker-docs.thinkingmachines.ai/tinker/api-reference/trainingclient/`
- SamplingClient API: `https://tinker-docs.thinkingmachines.ai/tinker/api-reference/samplingclient/`
- Weights/checkpoints: `https://tinker-docs.thinkingmachines.ai/tutorials/core-concepts/weights/`

## What RSIBench-Data Uses

RSIBench-Data does not ask the agent to write raw Tinker loops from scratch for
each attempt. The fixed wrapper owns the Tinker API calls:

```text
backend/tinker/train_lora_sft.py
backend/e2b_eval/   (eval: tool-call proxy sandbox + Tinker backend + Harbor)
```

The agent should focus on `train_messages.jsonl` and `run_config.json`.

## Core Tinker API Shape

Training:

```python
import tinker
from tinker import types

service = tinker.ServiceClient()
training = service.create_lora_training_client(
    base_model="Qwen/Qwen3.5-35B-A3B-Base",
    rank=8,
    seed=0,
)
tokenizer = training.get_tokenizer()

future = training.forward_backward(data, "cross_entropy")
result = future.result()
training.optim_step(types.AdamParams(learning_rate=1e-4)).result()

sampler = training.save_weights_for_sampler("my-run").result()
print(sampler.path)  # tinker://.../sampler_weights/...
```

Sampling from a trained checkpoint:

```python
sampling = service.create_sampling_client(model_path=sampler.path)
```

Sampling from the base model:

```python
sampling = service.create_sampling_client(base_model="Qwen/Qwen3.5-35B-A3B-Base")
```

## RSIBench-Data Wrapper Semantics

`backend/tinker/train_lora_sft.py` reads JSONL records like:

```json
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "...", "loss": true}]}
```

For each trainable assistant message, the wrapper:

1. Renders prior messages with the Qwen chat template.
2. Appends the selected assistant response tokens.
3. Builds the Tinker `Datum` from the full sequence using the standard
   right-shifted input / left-shifted target layout.
4. Sets CE `weights` to `0.0` on prompt positions and `1.0` on assistant
   response positions.
5. Runs Tinker LoRA SFT.
6. Saves a sampler checkpoint for eval.

## Cookbook Usage Guidance

The official `tinker-cookbook` package is installed for reference examples and
utility inspection. Agents may inspect it locally if useful:

```bash
python3 - <<'PY'
import inspect
import tinker_cookbook
print(tinker_cookbook.__file__)
PY
```

Do not replace the fixed RSIBench-Data training/eval chain with arbitrary
cookbook scripts. Use cookbook examples only to inform data format, masking,
checkpointing, or SFT design choices.
