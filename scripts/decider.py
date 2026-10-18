"""Download or serve the real, revision-pinned Decider without cloud access.

Run with .decider-venv/Scripts/python.exe on Windows (bin/python on Unix).
Downloads use .local/decider/huggingface; serving is offline and loopback-only.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".local" / "decider"
MODEL = "StrandsAgents/strands-decider-2B-qwen3.5-v1-2610"
MODEL_REVISION = "216d1ccb46a9e9b036eb9187b248db98480f77d4"
BASE = "Qwen/Qwen3.5-2B-Base"
BASE_REVISION = "b1485b2fa6dfa1287294f269f5fb618e03d52d7c"
MINIMUM_FREE_GIB = 12
GIB = 1024 ** 3


def environment() -> None:
    os.environ["HF_HOME"] = str(LOCAL / "huggingface")
    os.environ["HF_HUB_CACHE"] = str(LOCAL / "huggingface" / "hub")
    os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "60")
    os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "30")


def status() -> dict:
    import psutil

    versions = {}
    for name in ("strands-decider", "torch", "transformers", "peft", "huggingface-hub"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    available = psutil.virtual_memory().available / GIB
    record = LOCAL / "download.json"
    return {
        "packages": versions,
        "free_ram_gib": round(available, 2),
        "minimum_free_ram_gib": MINIMUM_FREE_GIB,
        "memory_guard_passed": available >= MINIMUM_FREE_GIB,
        "free_disk_gib": round(shutil.disk_usage(ROOT).free / GIB, 2),
        "download_record": json.loads(record.read_text()) if record.exists() else None,
        "inference_verified": False,
    }


def download() -> None:
    from huggingface_hub import snapshot_download

    if shutil.disk_usage(ROOT).free < 8 * GIB:
        raise RuntimeError("Need at least 8 GiB free disk for the pinned model and resumable downloads.")
    LOCAL.mkdir(parents=True, exist_ok=True)
    options = {"cache_dir": os.environ["HF_HUB_CACHE"], "token": False, "max_workers": 1}
    print("Downloading the real Decider adapter, head and tokenizer (~235 MB).", flush=True)
    checkpoint = snapshot_download(MODEL, revision=MODEL_REVISION, **options)
    print("Downloading its pinned Qwen base (~4.57 GB). No inference or cloud service is started.", flush=True)
    base = snapshot_download(BASE, revision=BASE_REVISION, **options)
    record = {"model": MODEL, "revision": MODEL_REVISION, "checkpoint": checkpoint,
              "base_model": BASE, "base_revision": BASE_REVISION, "base_snapshot": base}
    (LOCAL / "download.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2), flush=True)


def serve(port: int) -> int:
    current = status()
    if not current["memory_guard_passed"]:
        raise RuntimeError(
            f"CPU model not loaded: {current['free_ram_gib']} GiB RAM available; "
            f"the conservative startup guard requires {MINIMUM_FREE_GIB} GiB free physical RAM. "
            "A pagefile is not treated as available physical RAM."
        )
    record = current["download_record"]
    if not record or record.get("revision") != MODEL_REVISION or record.get("base_revision") != BASE_REVISION:
        raise RuntimeError("Pinned download is incomplete. Run this script with download first.")
    checkpoint = Path(record["checkpoint"])
    base = Path(record["base_snapshot"])
    required = [checkpoint / "strands_decider_config.json", checkpoint / "head.safetensors",
                checkpoint / "lora" / "adapter_model.safetensors",
                base / "model.safetensors-00001-of-00001.safetensors"]
    if not all(path.is_file() for path in required):
        raise RuntimeError("A required cached model file is missing. Rerun download to repair the cache.")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ.setdefault("OMP_NUM_THREADS", "4")
    os.environ.setdefault("MKL_NUM_THREADS", "4")
    executable = Path(sys.executable).parent / ("strands-decider.exe" if os.name == "nt" else "strands-decider")
    if not executable.is_file():
        raise RuntimeError("Use the isolated .decider-venv Python interpreter with strands-decider installed.")
    command = [str(executable), "serve", str(checkpoint), "--device", "cpu", "--host", "127.0.0.1",
               "--port", str(port), "--model-name", MODEL, "--strict-window", "--max-batch", "1",
               "--no-prefix-cache"]
    print(f"Starting real CPU inference on http://127.0.0.1:{port}; keep this terminal running.", flush=True)
    return subprocess.call(command, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("download", "status", "serve"))
    parser.add_argument("--port", type=int, default=8099)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    environment()
    try:
        if args.action == "status":
            print(json.dumps(status(), indent=2))
        elif args.action == "download":
            download()
        else:
            return serve(args.port)
        return 0
    except (ImportError, RuntimeError, OSError, ValueError) as exc:
        print(f"Decider setup: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
