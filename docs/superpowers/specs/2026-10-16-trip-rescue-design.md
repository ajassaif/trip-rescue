# Trip Rescue

Approved concept: a travel recovery agent for the AWS Strands Decider hackathon. Build in this separate sibling folder, preserving Rosses Ananda.

## Experience

A desktop recovery desk with pale blue map paper (#edf3f6), navy ink (#183446), white panels, teal routes (#117a77), and orange disruption markers (#c85226). Barlow Condensed headings, Public Sans body, IBM Plex Mono measurements. A schematic Kerala route map is the signature, explicitly labeled as illustrative. Mobile stacks trip input, map, results, and trace. Keyboard focus, semantic forms, reduced motion, and announced errors are required.

Users choose cancelled train, missed flight, or monsoon disruption; edit their message, locations, budget, deadline and scenario time; then run recovery. The output shows feasible options, an explanation, a decision log, and a downloadable JSON trace. No bookings or messages are sent. Travel inventory and disruption reports are fictional fixtures even with live models. Filters enforce route, cost, departure after scenario time, and arrival before deadline, with no fabricated inventory for unsupported routes.

## Agent

Python FastAPI owns the workflow in backend/app.py, with models.py, inventory.py, config.py, and providers.py alongside it. Demo mode uses explicit deterministic rules with null model confidence and no claimed model latency. Live mode requires STRANDS_DECIDER_URL, BEDROCK_MODEL_ID and AWS credentials. A reusable choice question selects find_transport, find_stay, check_disruptions, or clarify. Returned choices and numeric confidence must validate. A threshold of 0.8 initially controls whether the agent asks for clarification; this is a configurable heuristic requiring evaluation, not an accuracy guarantee. No tool runs if input is incomplete, response is malformed or confidence is low. Bedrock Converse writes a brief explanation from tool evidence only. Failures never silently fall back to demo. Service calls have finite timeouts. The endpoint reports separate provenance for decision, explanation and inventory.

Next.js App Router provides the dashboard and same-origin API proxy to FastAPI. Credentials remain on the server. The local demo binds to loopback. AWS deployment uses containers in a private demo environment, with a deployment guide and explicit readiness checklist. No paid deployment or publication in this build.

## Interface

POST /api/rescue proxies POST /rescue. Request: {mode: 'demo'|'live', scenario: 'rail'|'flight'|'weather', message: string, origin: string, destination: string, budget: number, current_time: 'HH:mm', arrive_by: 'HH:mm'}; all times are the same fictional day, IST. GET /api/health proxies /health.

Response: {id: string, mode: 'demo'|'live', status: 'ready'|'clarify'|'no_options', summary: string, question: string|null, selected_tool: string, decision: {choice: string, confidence: number|null, latency_ms: number|null, source: string, model: string|null, probabilities: Record<string, number>}, options: [{id: string, kind: 'bus'|'train'|'taxi'|'stay'|'advisory', title: string, subtitle: string, departure: string|null, arrival: string|null, duration_minutes: number|null, cost: number|null, tags: string[], steps: string[]}], trace: [{stage: string, title: string, detail: string, duration_ms: number|null}], provenance: {decision: string, explanation: string, inventory: string}, total_ms: number}.

Errors: non-2xx {detail: string}. Health: {status:'ok', live_configured: boolean, missing: string[], inventory:'fixtures'}; configured does not mean a successful live call.

## Verification and delivery

Test all three scenarios, budget/deadline exclusion, missing and unsupported routes, low confidence, invalid choice, service failures, Bedrock grounding payload, and API validation. Verify frontend production build, lint, types, desktop and narrow mobile flow. Deliver runnable source, locked app dependencies, reusable recipe, Docker files, AWS guide, article draft, and a sub-three-minute recording script. Claim live integration or AWS deployment only after observing successful runs.
