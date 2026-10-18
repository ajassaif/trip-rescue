# Verification — updated 18 October 2026

## Observed locally

| Check | Result |
| --- | --- |
| Python backend tests | 63 passed; one upstream Starlette HTTPX test-client deprecation warning |
| Backend dependency consistency | `pip check` passed |
| ESLint | Passed |
| TypeScript | Passed |
| Next.js production build | Passed; `/`, `/icon.svg`, `/api/health`, `/api/rescue` generated |
| Same-origin API smoke checks | Seven passed through the running Next.js proxy |
| Docker Compose configuration | `docker compose config --quiet` passed |

The smoke checks use `npm run test:smoke` with the app running. They verify the three tools, unaffordable inventory, missing origin, foreign Origin rejection, and invalid time-window errors. Node 24 prints a harmless module-type detection warning when importing the TypeScript scenario fixture into the smoke script.

## Browser observations

- Train scenario returned three fictional alternatives, with absent demo confidence/model latency.
- Missed-flight scenario returned two overnight stays in Kochi, explicitly excluding onward travel to Bengaluru.
- Monsoon scenario returned fictional reports without fares, travel times or arrival guarantees.
- A ₹100 train budget returned no matching options.
- An empty origin paused for clarification, with no tool stage in the trace.
- JSON export downloaded successfully; its parsed contents included the request, mode, selected tool, three options and fictional-inventory provenance.
- Help dialog opened and Escape dismissed it, returning focus to the initiating button.
- Mobile at 390×844 and desktop at 1440×1000 were visually inspected. Document width did not exceed viewport width in either case. Temporary viewport overrides were reset.
- No browser console errors were recorded in the final inspected run.

Screenshots: [desktop](screenshots/desktop.jpg), [mobile](screenshots/mobile.jpg). They show demo-mode fixture data.

## Issues found and resolved

- Browser requests were initially rejected because Next.js normalized the internal request URL to localhost. Origin validation now checks the incoming browser-facing Host, and both allowed/rejected origins pass smoke checks.
- Inventory contained inaccurate ranking tags and past meeting deadlines. Tags were removed and pickup steps no longer contain impossible past prerequisites. The fixtures assume the traveler can reach the departure point; travel-to-pickup and boarding cutoffs are not modeled.
- An enormous JSON integer in Decider confidence/probabilities could raise OverflowError. Range validation now precedes finite-number conversion. Regressions prove a structured 502 and no tool/Bedrock execution.
- Long custom location labels could clip. SVG labels are shortened and the journey strip wraps; accessible map text retains the full request locations.

An independent source reviewer approved the local-demo scope after the numeric-validation and label fixes.

## Not verified

- AWS hosting of Decider and the agent API. A temporary EC2 stack was created, but the agent and model were not installed/tested there. The stack and all five resources were deleted on 18 October at the user's request; see [cleanup record](aws-cleanup.md). Bedrock inference from the local agent was verified on 17 October.
- Docker images or runtime. Docker was stopped to release memory. Compose configuration validation alone does not establish container execution success.
- Real travel availability, route safety, fares or weather. There is no live travel-data provider.
- A live-model quality, calibration, cost or latency comparison. The examples below are individual observations, not a benchmark or accuracy estimate.

The API and frontend are intended for private demo use and do not implement public-user authentication. Deployment and submission steps are documented separately.

## Actual model runs — 17 October 2026

The running local CPU endpoint identified `StrandsAgents/strands-decider-2B-qwen3.5-v1-2610`, using `Qwen/Qwen3.5-2B-Base`. Trip Rescue reused that already-running service instead of loading a second model on the 16 GB laptop. The API and UI ran locally; explanations used real Amazon Bedrock `amazon.nova-micro-v1:0` in `us-east-1`. The approved temporary bearer key stays only in ignored local configuration.

| Scenario | Actual choice | Confidence | Decider HTTP time | Outcome |
| --- | --- | --- | --- | --- |
| Cancelled train | `find_transport` | 0.9809 | 24,279.10 ms | Three options; UI and JSON export verified |
| Missed flight | `find_stay` | 0.9849 | 42,898.27 ms | Two Kochi stays; onward travel excluded |
| Monsoon | `check_disruptions` | 0.9780 | 14,597.68 ms | Two reports; no invented safe-route or arrival guarantee |

All three responses contained live Decider and Bedrock provenance. All inventory remains fictional. Their explanations were reviewed against the returned evidence. The rail screenshot is [live-rail.jpg](screenshots/live-rail.jpg); sanitized fixture-only JSON evidence is in [evidence/](evidence/).

The first live rail explanation incorrectly claimed no options fit despite three filtered options. The explanation prompt now supplies a result-specific instruction, temperature is zero, and a narrow guard rejects that observed contradiction. A regression test covers it. This is not a general factuality guarantee; review generated explanations before acting on them.

The separate pinned local-model download also completed. Its revision record describes those downloaded files, not proof that the reused service loaded exactly the same cached revision. No second local model process was started.
