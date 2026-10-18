from time import perf_counter
from uuid import uuid4
import re

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.config import Settings
from backend.inventory import run_tool
from backend.models import DecisionView, Provenance, RescueRequest, RescueResponse, TraceEvent
from backend.providers import BedrockExplainer, ExplanationError
from patterns.tool_selection import DeciderClient, DecisionError


def demo_choice(request: RescueRequest) -> str:
    message = request.message.casefold()
    if re.search(r"\b(?:hotel|accommodation|somewhere tonight|somewhere to stay|room|stay|sleep)\b", message):
        return "find_stay"
    if request.scenario == "weather" or re.search(r"\b(?:monsoon|flood|rain|closure|disruption|weather)\b", message):
        return "check_disruptions"
    return "find_transport"


def create_app(*, settings: Settings | None = None, decider=None, explainer=None):
    settings = settings if settings is not None else Settings.from_env()
    app = FastAPI(title="Trip Rescue", version="1.0.0", description="Private demo. All travel inventory is fictional.")

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request, exc):
        details = []
        for error in exc.errors():
            field = ".".join(str(part) for part in error["loc"] if part != "body") or "request"
            details.append(f"{field}: {error['msg']}")
        return JSONResponse(status_code=422, content={"detail": "; ".join(details)})

    @app.get("/health")
    def health():
        missing = settings.missing()
        return {"status": "ok", "live_configured": not missing, "missing": missing, "inventory": "fixtures"}

    @app.post("/rescue", response_model=RescueResponse)
    def rescue(request: RescueRequest):
        started = perf_counter()
        trace = [TraceEvent(stage="input", title="Read recovery request", detail="All times use the same fictional day in IST. Budget is in INR.")]

        def result(status, decision, options, summary, question=None, selected_tool=None, explanation_source="deterministic demo template"):
            return RescueResponse(
                id=str(uuid4()), mode=request.mode, status=status, summary=summary, question=question,
                selected_tool=selected_tool or decision.choice, decision=decision, options=options, trace=trace,
                provenance=Provenance(decision=decision.source, explanation=explanation_source),
                total_ms=round((perf_counter() - started) * 1000, 2),
            )

        missing = [field for field in ("message", "origin", "destination") if not getattr(request, field)]
        if missing:
            decision = DecisionView(choice="clarify", source="input validation")
            trace.append(TraceEvent(stage="gate", title="More information needed", detail="Missing " + ", ".join(missing) + ". No model or tool was called."))
            return result("clarify", decision, [], "I need a few trip details before selecting a recovery tool.",
                          question="Please provide " + ", ".join(missing) + ".", explanation_source="input validation")

        if request.mode == "demo":
            decision = DecisionView(choice=demo_choice(request), source="deterministic demo rules")
            trace.append(TraceEvent(stage="decision", title="Demo rule selected a tool", detail=f"Selected {decision.choice}. No model inference, model confidence or model latency is claimed."))
        else:
            if settings.missing():
                raise HTTPException(503, "Live mode is not configured. Missing: " + ", ".join(settings.missing()))
            provider = decider or DeciderClient(settings.decider_url, timeout=settings.provider_timeout_seconds, model=settings.decider_model)
            try:
                chosen = provider.select(request.model_dump() | {"time_zone": "IST", "inventory": "fictional fixtures"})
            except DecisionError as exc:
                raise HTTPException(502, str(exc)) from exc
            decision = DecisionView(choice=chosen.choice, confidence=chosen.confidence, latency_ms=chosen.latency_ms,
                                    source="Strands Decider live HTTP", model=chosen.model, probabilities=chosen.probabilities)
            trace.append(TraceEvent(stage="decision", title="Strands Decider selected a tool", detail=f"Validated typed choice: {chosen.choice}.", duration_ms=chosen.latency_ms))
            if chosen.confidence < settings.confidence_threshold or chosen.choice == "clarify":
                trace.append(TraceEvent(stage="gate", title="Ask before acting", detail=f"Choice was clarify or confidence was below the configured {settings.confidence_threshold:.2f} threshold. No tool ran."))
                return result("clarify", decision, [], "Please clarify your immediate recovery need before I continue.",
                              question="Do you need onward transport, a place to stay tonight, or a disruption report?",
                              selected_tool="clarify", explanation_source="confidence gate template")
            trace.append(TraceEvent(stage="gate", title="Confidence gate passed", detail=f"Confidence met {settings.confidence_threshold:.2f}. This heuristic is not an accuracy guarantee."))

        tool_started = perf_counter()
        options = run_tool(decision.choice, request)
        trace.append(TraceEvent(stage="tool", title=f"Ran {decision.choice}", detail=f"Returned {len(options)} fictional option(s) after route, fare and applicable same-day schedule filters. Advisories have no travel schedule.", duration_ms=round((perf_counter() - tool_started) * 1000, 2)))
        status = "ready" if options else "no_options"
        if request.mode == "demo":
            if not options:
                summary = "No fictional inventory fits this route and these constraints. Try another budget or time window, or use one of the supported scenario routes. Nothing is booked."
            elif decision.choice == "find_stay":
                summary = f"Found {len(options)} fictional stays in {request.origin} within your budget, with check-in before your deadline. These are overnight recovery options; they do not get you to {request.destination}. Nothing is booked."
            elif decision.choice == "check_disruptions":
                summary = "Review these fictional disruption reports before planning the next leg. They are not current alerts and do not confirm a safe route or an on-time arrival."
            else:
                summary = f"Found {len(options)} fictional alternatives from {request.origin} to {request.destination} within your budget and arrival deadline. Compare cost and timing; nothing is booked."
            explanation_source = "deterministic demo template"
            trace.append(TraceEvent(stage="explanation", title="Prepared demo explanation", detail="Template generated from filtered fixture results; no language model used."))
        else:
            explain_started = perf_counter()
            evidence = {"inventory": "fictional fixtures", "selected_tool": decision.choice, "status": status,
                        "constraints": request.model_dump(exclude={"message", "mode"}) | {"time_zone": "IST"},
                        "options": [option.model_dump() for option in options]}
            try:
                summary = (explainer or BedrockExplainer(settings)).explain(evidence)
            except ExplanationError as exc:
                raise HTTPException(502, str(exc)) from exc
            explanation_source = "Amazon Bedrock Converse live"
            trace.append(TraceEvent(stage="explanation", title="Bedrock explained the evidence", detail=f"Model {settings.bedrock_model_id} received only filtered fictional inventory and trip constraints.", duration_ms=round((perf_counter() - explain_started) * 1000, 2)))
        return result(status, decision, options, summary, explanation_source=explanation_source)

    return app


app = create_app()
