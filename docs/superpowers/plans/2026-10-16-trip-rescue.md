# Trip Rescue Implementation Plan

> **For agentic workers:** Use subagent-driven-development for the independent backend task and scoped review. Keep implementation inside this new project.

**Goal:** Deliver a runnable travel recovery demo with real Decider and Bedrock integration paths.

**Architecture:** Next.js dashboard proxies a Python agent. Python routes one bounded tool decision, filters fictional inventory, and explains the evidence. Demo and live execution have distinct provenance.

**Tech Stack:** Next.js 16, React 19, TypeScript, FastAPI, boto3, pytest.

**Spec:** ../specs/2026-10-16-trip-rescue-design.md

## Global Constraints

- No changes to Rosses Ananda.
- Travel inventory is fictional in both modes.
- No silent live-to-demo fallback and no fake measured model metrics.
- No cloud deployment or public publishing during local implementation.

## Task 1: Agent and reusable recipe

Files: backend/{app,models,config,inventory,providers}.py, backend/tests/test_rescue.py, patterns/tool_selection.py, patterns/README.md, backend/requirements.txt, backend/Dockerfile.

Consumes the request and produces the response defined in the spec. Implement `rescue(request)` and a reusable typed question plus choice validator. Place the decision before dispatch; validate all outcomes. Use dependency injection for providers in tests. Validate response bodies with Pydantic. Bound model timeouts and return explicit errors.

- [x] Implement fixtures, routing and live adapters.
- [x] Verify pytest covers correct tool execution, constraints and service failures.
- [x] Review backend against the contract and fix findings.

## Task 2: Recovery dashboard

Files: package.json, src/app/{layout,page,globals.css}, src/app/api/{rescue,health}/route.ts, src/components/{rescue-desk,route-map,decision-log,recovery-results}.tsx, src/lib/{types,scenarios}.ts.

Consumes the API contract. Show scenario input, illustrated route, recovery options, provenance and trace; implement loading, error, clarification and export. Use `fetch('/api/rescue', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request)})` with timeout and disabled controls during execution. Clear stale results when input changes.

- [x] Build responsive UI and same-origin proxy.
- [x] Run `npm run lint`, `npm run typecheck`, and `npm run build`.
- [x] Exercise three scenarios, empty results, export, keyboard and mobile in browser.

## Task 3: Run and submission package

Files: README.md, .env.example, Dockerfile, compose.yaml, docs/{aws-deployment,article-draft,demo-script,verification}.md, scripts/dev.mjs.

- [x] Provide one-command local launch and two-container deployment definition.
- [x] Document actual configuration, AWS private access and verification steps.
- [x] Write article and timed demo script without invented live measurements.
- [x] Review integrated app, fix defects and record observed validation results.
