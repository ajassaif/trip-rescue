# Typed tool selection with Strands Decider

`tool_selection.py` is a reusable, synchronous HTTP recipe. It requires only `httpx` and Python 3.11+. Copy it into another application and provide your own state and named criteria. It does not download a model or execute tools.

```python
from patterns.tool_selection import DeciderClient, TOOL_CRITERIA

client = DeciderClient("http://127.0.0.1:8099", timeout=30)
decision = client.select({"message": "My train was cancelled"})
if decision.confidence >= 0.8 and decision.choice != "clarify":
    print("Candidate tool:", decision.choice)
else:
    print("Ask a clarifying question before running any tool")
```

For another domain, pass `criteria={"search": "...", "clarify": "..."}` and your own `instructions` to `DeciderClient`. The request is `POST /v1/systemone` with a named `next_tool` question of `type: choice`. The response is validated before the caller receives a decision: choice must be allowed; confidence and every probability must be finite numbers between zero and one; the probability keys must match the criteria and sum approximately to one; and the choice must have maximum probability. Numeric strings and booleans are rejected. No upstream error text is exposed and failures never substitute a demo decision.

Confidence is the provider's normalized concentration measure, not an empirical probability of correctness. `0.8` is a configurable initial abstention heuristic that needs evaluation on your use case. Do not derive it from latency or hardcode confidence for a rule-based example. Apply input validation and any authorization checks before calling a tool. Keep the tool registry separate from model output and never dynamically import or execute a returned name.

Trip Rescue uses the four `TOOL_CRITERIA` defaults, checks input before inference, gates tool execution on confidence, and calls Bedrock only after filtering fictional tool evidence. Transport and hotel fixtures are never live inventory.

Protocol references: [official schema](https://github.com/strands-labs/strands-decider/blob/main/src/strands_decider/schema.py) and [official HTTP example](https://github.com/strands-labs/strands-decider/blob/main/examples/strands/_client.py). The default model request is `StrandsAgents/strands-decider-2B-qwen3.5-v1-2610`; the response's actual model identifier is retained. The server determines the loaded checkpoint. Deploy the Decider separately using its official instructions; this repository does not bundle model weights.
