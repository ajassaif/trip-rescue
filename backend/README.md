# Recovery API

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.lock
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8100
```

Run the suite with `.\.venv\Scripts\python.exe -m pytest backend/tests -q`. On macOS/Linux use `.venv/bin/python`. Build the backend container from the repository root: `docker build -f backend/Dockerfile -t trip-rescue-api .`.

`requirements.txt` records direct dependencies; `requirements.lock` pins the complete tested environment. The current Starlette test client emits a deprecation warning about its HTTPX adapter; the production Decider adapter uses HTTPX directly and all tests pass.

`POST /rescue` accepts the contract in the design specification. `GET /health` reports configuration only; it does not contact Decider or Bedrock or prove credentials are valid. Interactive API documentation is at `/docs` for local development.

Demo mode requires no credentials. Live mode requires `STRANDS_DECIDER_URL`, `BEDROCK_MODEL_ID`, and an AWS credential source. Standard AWS static environment credentials, a configured profile, an existing default credentials file, container credentials, or web identity may be used. Set `AWS_USE_INSTANCE_ROLE=true` explicitly for EC2 instance-profile credentials. Configure `AWS_REGION` (default `ap-south-1`). AWS credentials stay on the server. This API is for a private demo environment and has no built-in authentication; keep its port private.

Optional settings: `STRANDS_DECIDER_MODEL` (default `StrandsAgents/strands-decider-2B-qwen3.5-v1-2610`), `DECIDER_CONFIDENCE_THRESHOLD` (default `0.8`, finite number from 0 to 1), and `PROVIDER_TIMEOUT_SECONDS` (default `30`, finite number from 1 to 60). Model calls have finite connect/read timeouts and disabled automatic SDK retries. Upstream failures return non-2xx JSON with a string `detail`; the API never silently falls back to demo mode. Model confidence remains the Decider response's score; it is not presented as calibrated accuracy.

All options and reports are fictional inventory, in both modes. Only the three exact scenario routes have fixture coverage: rail Varkala–Kochi, flight Kochi–Bengaluru, and weather Munnar–Kochi. Matching ignores case and outer whitespace. No external travel API or booking system is connected. Hotel times mean transfer departure and check-in in Kochi, not arrival in Bengaluru. Disruption advisories have no fare or travel schedule and make no claim that a journey meets the arrival deadline. Their route scope is still enforced. Transport and stays enforce cost, departure strictly after scenario time, and arrival/check-in at or before the same-day IST deadline. Overnight journeys are not supported.

The server preflights missing text and route fields before any inference. In live mode, low confidence or a `clarify` choice prevents tool execution and Bedrock explanation. Model responses with invalid choices, types, or probabilities are errors. For successful selection, a local allowlist dispatches a fixture tool and deterministic filtering runs before Bedrock receives evidence. The explanation prompt excludes the user's raw free-form message and instructs Bedrock to use only filtered evidence. This grounding reduces invention but does not prove every generated sentence is factual; inspect model outputs during evaluation.

Fixture schedules start at the stated departure point. Travel time to that point and operator boarding cutoffs are not modeled; steps do not add separate fixed meeting deadlines. Static tags describe service attributes and do not rank options by price or arrival time.

Tests inject HTTP transport and a Bedrock client, exercising the real adapters and their payloads without paid calls. Passing these tests is not a claim of a successful live model call or AWS deployment.
