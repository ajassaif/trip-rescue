"""Run inside the Decider virtual environment on the temporary test host."""

from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import platform
from urllib.request import urlopen

import psutil

with urlopen("http://127.0.0.1:8099/health", timeout=5) as response:
    health = json.load(response)
metadata = {
    "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
    "deployment": "AWS EC2 c7i.2xlarge, us-east-1; local UI over SSH tunnel",
    "operating_system": platform.freedesktop_os_release().get("PRETTY_NAME"),
    "python": platform.python_version(),
    "logical_cpus": psutil.cpu_count(),
    "memory_bytes": psutil.virtual_memory().total,
    "bedrock_model": "amazon.nova-micro-v1:0",
    "bedrock_credentials": "EC2 instance role restricted to regional Nova Micro InvokeModel",
    "decider_health": health,
    "packages": {name: version(name) for name in
                 ("strands-decider", "torch", "transformers", "peft", "huggingface-hub")},
    "downloaded_model_revisions": {
        path.parent.name: sorted(entry.name for entry in path.iterdir() if entry.is_dir())
        for path in (Path.home() / ".cache/huggingface/hub").glob("models--*/snapshots")
    },
    "limitations": "Four live examples are not a benchmark or accuracy estimate. Travel inventory is fictional.",
}
print(json.dumps(metadata, indent=2))
