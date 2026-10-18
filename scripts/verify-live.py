"""Run bounded live examples; preserve responses without claiming an accuracy benchmark."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser()
parser.add_argument("--base-url", default="http://127.0.0.1:18100")
parser.add_argument("--requests", required=True, type=Path)
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)

requests = json.loads(args.requests.read_text(encoding="utf-8-sig"))
for name, body in requests.items():
    body["mode"] = "live"
    started = datetime.now(timezone.utc).isoformat()
    request = Request(args.base_url.rstrip("/") + "/rescue",
                      data=json.dumps(body).encode(),
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=130) as response:
        result = json.load(response)
    evidence = {"recorded_at_utc": started, "request": body, "result": result}
    (args.output / f"{name}.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert result["mode"] == "live"
    assert result["provenance"]["decision"] == "Strands Decider live HTTP"
    if result["status"] != "clarify":
        assert result["provenance"]["explanation"] == "Amazon Bedrock Converse live"
    print(json.dumps({"scenario": name, "status": result["status"],
                      "tool": result["selected_tool"],
                      "confidence": result["decision"]["confidence"],
                      "decider_ms": result["decision"]["latency_ms"],
                      "options": len(result["options"]),
                      "summary": result["summary"]}, ensure_ascii=False), flush=True)
