# Local Strands Decider

This setup uses the real published decision model, separate from Trip Rescue's lightweight API environment. Downloading files does not perform inference, start AWS resources, or incur model API charges. Travel inventory remains fictional even when a real model selects the tool.

## Reproduce on Windows

From the repository root, with Python 3.12:

```powershell
python -m venv .decider-venv
.\.decider-venv\Scripts\python.exe -m pip install -r scripts/decider-requirements.lock
.\.decider-venv\Scripts\python.exe scripts/decider.py status
.\.decider-venv\Scripts\python.exe scripts/decider.py download
.\.decider-venv\Scripts\python.exe scripts/decider.py serve
```

On Linux, use `.decider-venv/bin/python`. The dependency lock records the tested Windows Python environment; Linux users should choose an appropriate CPU-only PyTorch wheel using [PyTorch's official installation selector](https://pytorch.org/get-started/locally/) before installing matching remaining dependencies. No GPU, CUDA extension, or training dependencies are required for this CPU path.

The download command uses public repositories with `token=False`, pins both model revisions, and uses Hugging Face's resumable cache. Rerun it after an interrupted download; existing completed files are reused. Files stay under ignored `.local/decider/huggingface/`. A completion record is written to `.local/decider/download.json` only after both snapshots finish. A download is not a verified inference result.

| Component | Repository | Pinned revision |
| --- | --- | --- |
| Adapter, pointer head and tokenizer | `StrandsAgents/strands-decider-2B-qwen3.5-v1-2610` | `216d1ccb46a9e9b036eb9187b248db98480f77d4` |
| Base model | `Qwen/Qwen3.5-2B-Base` | `b1485b2fa6dfa1287294f269f5fb618e03d52d7c` |

The base revision comes from the published Decider checkpoint's `provenance.json`. The base weights alone are 4,548,221,488 bytes; adapter weights are 201,878,888 bytes; pointer-head weights are 12,605,928 bytes. Tokenizers and metadata add more. Allow roughly 4.8 GB of downloads and at least 8 GiB free disk for this workflow. Network speed determines download time.

## Memory and serving

The upstream CPU engine converts its torso to float32. Upstream describes approximately 7 GiB for torso weights alone, before adapter, activations, temporary conversion buffers, and the Python runtime. The startup script conservatively requires **12 GiB free physical RAM**, checking before importing or loading the model. A pagefile does not satisfy that requirement. This is a protective estimate, not a guarantee that every context length will fit.

At setup inspection on 17 October 2026, this 16 GB laptop had approximately 2.5 GiB free physical RAM while the application was running. The startup guard rejected loading a new process. Both pinned downloads subsequently completed. An already-running local Decider service was then discovered and reused: all three Trip Rescue scenarios passed with real inference and Bedrock explanations. That existing service was left untouched. Do not start a second model process while memory is constrained; see the [verification record](verification.md) for the distinction between downloaded revisions and the reused endpoint.

Serving is explicitly CPU, binds only `127.0.0.1:8099`, limits batch size to one, disables prefix caching, and rejects oversized prompts. It runs with Hugging Face and Transformers offline mode, so a missing cached file fails instead of initiating another download. Keep the serving terminal open; Ctrl+C stops it. Use `--port` to choose another local port.

After the process reports ready, inspect `http://127.0.0.1:8099/health` and make a typed choice request to `/v1/systemone`. A health response alone does not verify a successful choice. Trip Rescue can use this endpoint as `STRANDS_DECIDER_URL`, but its current full live workflow also requires a configured Bedrock model and AWS credentials; running Decider locally does not by itself complete that live workflow. The setup script never edits `.env` or provides a demo fallback.

## References

- [Official inference guide](https://github.com/strands-labs/strands-decider/blob/main/docs/inference.md)
- [CPU float32 conversion implementation](https://github.com/strands-labs/strands-decider/blob/main/src/strands_decider/infer.py)
- [Published Decider snapshot](https://huggingface.co/StrandsAgents/strands-decider-2B-qwen3.5-v1-2610/tree/216d1ccb46a9e9b036eb9187b248db98480f77d4)
- [Pinned Qwen base snapshot](https://huggingface.co/Qwen/Qwen3.5-2B-Base/tree/b1485b2fa6dfa1287294f269f5fb618e03d52d7c)
