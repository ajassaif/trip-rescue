import json
import re

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.app import create_app
from backend.config import Settings
from backend.models import minutes
from backend.providers import BedrockExplainer
from patterns.tool_selection import DeciderClient, DecisionError, validate_answer


RAIL = dict(mode="demo", scenario="rail", message="My train was cancelled. Get me to Kochi.", origin="Varkala", destination="Kochi", budget=3000, current_time="14:30", arrive_by="21:00")
FLIGHT = dict(mode="demo", scenario="flight", message="I missed the last flight and need somewhere tonight.", origin="Kochi", destination="Bengaluru", budget=5000, current_time="18:15", arrive_by="23:30")
WEATHER = dict(mode="demo", scenario="weather", message="Monsoon rain has blocked my route. Check disruptions.", origin="Munnar", destination="Kochi", budget=2500, current_time="15:00", arrive_by="22:00")


def wire(choice="find_transport", confidence=0.94):
    probabilities = {key: (0.955 if key == choice else 0.015) for key in ("find_transport", "find_stay", "check_disruptions", "clarify")}
    return {"model": "test-decider", "answers": {"next_tool": {"type": "choice", "choice": choice, "confidence": confidence, "probabilities": probabilities}}}


class FakeBedrock:
    def __init__(self, response=None, error=None):
        self.requests = []
        self.response = response or {"output": {"message": {"content": [{"text": "These fictional options fit the supplied constraints."}]}}}
        self.error = error

    def converse(self, **kwargs):
        self.requests.append(kwargs)
        if self.error:
            raise self.error
        return self.response


def live_client(payload=None, http_status=200, bedrock=None, threshold=0.8):
    requests = []
    def respond(request):
        requests.append(request)
        return httpx.Response(http_status, json=payload or wire())
    decider = DeciderClient("http://decider.test", client=httpx.Client(transport=httpx.MockTransport(respond)))
    bedrock = bedrock or FakeBedrock()
    settings = Settings(decider_url="http://decider.test", bedrock_model_id="test-bedrock", credentials_configured=True, confidence_threshold=threshold)
    app = create_app(settings=settings, decider=decider, explainer=BedrockExplainer(settings, client=bedrock))
    return TestClient(app), requests, bedrock


@pytest.mark.parametrize("trip,choice,kind", [(RAIL, "find_transport", "bus"), (FLIGHT, "find_stay", "stay"), (WEATHER, "check_disruptions", "advisory")])
def test_demo_scenarios_are_explicit_fixtures(trip, choice, kind):
    result = TestClient(create_app()).post("/rescue", json=trip)
    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "ready"
    assert body["selected_tool"] == choice
    assert any(option["kind"] == kind for option in body["options"])
    assert body["decision"]["confidence"] is None
    assert body["decision"]["latency_ms"] is None
    assert body["decision"]["model"] is None
    assert body["provenance"]["inventory"] == "fictional fixtures"
    assert body["provenance"]["decision"] == "deterministic demo rules"


@pytest.mark.parametrize("changes", [{"budget": 10}, {"arrive_by": "15:00"}, {"current_time": "20:30"}, {"origin": "Delhi"}, {"destination": "Mumbai"}])
def test_constraints_and_unsupported_routes_never_invent_stock(changes):
    body = TestClient(create_app()).post("/rescue", json=RAIL | changes).json()
    assert body["status"] == "no_options"
    assert body["options"] == []


def test_departure_must_be_strictly_after_now_and_arrival_at_deadline_is_allowed():
    client = TestClient(create_app())
    options = client.post("/rescue", json=RAIL).json()["options"]
    bus = next(option for option in options if option["kind"] == "bus")
    at_deadline = client.post("/rescue", json=RAIL | {"arrive_by": bus["arrival"], "budget": bus["cost"]}).json()
    assert bus["id"] in [option["id"] for option in at_deadline["options"]]
    at_departure = client.post("/rescue", json=RAIL | {"current_time": bus["departure"]}).json()
    assert bus["id"] not in [option["id"] for option in at_departure["options"]]


@pytest.mark.parametrize("current_time", ["14:55", "15:05"])
def test_returned_rail_steps_never_require_an_already_missed_time(current_time):
    body = TestClient(create_app()).post("/rescue", json=RAIL | {"current_time": current_time, "budget": 5000}).json()
    assert body["options"]
    for option in body["options"]:
        for step in option["steps"]:
            for scheduled_time in re.findall(r"\b\d{2}:\d{2}\b", step):
                assert minutes(scheduled_time) > minutes(current_time), (option["id"], step)


@pytest.mark.parametrize("trip", [FLIGHT, WEATHER])
def test_stays_and_advisories_do_not_bypass_route_scope(trip):
    body = TestClient(create_app()).post("/rescue", json=trip | {"origin": "Delhi"}).json()
    assert body["status"] == "no_options"
    assert body["options"] == []


def test_missing_input_clarifies_before_any_provider_call():
    client, requests, bedrock = live_client()
    body = client.post("/rescue", json=RAIL | {"mode": "live", "origin": " "}).json()
    assert body["status"] == "clarify"
    assert body["question"]
    assert requests == [] and bedrock.requests == []


def test_live_wiring_sends_typed_choice_and_grounded_evidence_to_bedrock():
    client, requests, bedrock = live_client()
    response = client.post("/rescue", json=RAIL | {"mode": "live"})
    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["model"] == "test-decider"
    assert body["decision"]["confidence"] == 0.94
    assert body["decision"]["latency_ms"] >= 0
    assert requests[0].url.path == "/v1/systemone"
    question = json.loads(requests[0].content)["questions"]["next_tool"]
    assert question["type"] == "choice"
    assert set(question["criteria"]) == {"find_transport", "find_stay", "check_disruptions", "clarify"}
    prompt = json.loads(bedrock.requests[0]["messages"][0]["content"][0]["text"].split("\nTool evidence:\n", 1)[1])
    assert prompt["options"] == body["options"]
    assert prompt["inventory"] == "fictional fixtures"
    assert bedrock.requests[0]["modelId"] == "test-bedrock"
    assert "Never invent" in bedrock.requests[0]["system"][0]["text"]


@pytest.mark.parametrize("confidence", [0.79, 0.0])
def test_low_confidence_prevents_tool_execution_and_explanation(confidence):
    client, _, bedrock = live_client(wire(confidence=confidence))
    body = client.post("/rescue", json=RAIL | {"mode": "live"}).json()
    assert body["status"] == "clarify"
    assert body["selected_tool"] == "clarify"
    assert body["options"] == []
    assert bedrock.requests == []
    assert not any(stage["stage"] == "tool" for stage in body["trace"])


def test_confidence_threshold_is_configurable():
    client, _, _ = live_client(wire(confidence=0.7), threshold=0.65)
    assert client.post("/rescue", json=RAIL | {"mode": "live"}).json()["status"] == "ready"


@pytest.mark.parametrize("bad", ["0.9", True, None, -0.1, 1.1, float("nan")])
def test_reusable_recipe_rejects_invalid_confidence(bad):
    with pytest.raises(DecisionError):
        validate_answer(wire(confidence=bad))


@pytest.mark.parametrize("mutation", ["choice", "missing", "probabilities", "type"])
def test_malformed_decider_response_is_error_without_fallback(mutation):
    payload = wire()
    answer = payload["answers"]["next_tool"]
    if mutation == "choice": answer["choice"] = "book_flight"
    if mutation == "missing": del answer["confidence"]
    if mutation == "probabilities": answer["probabilities"] = {"find_transport": 1}
    if mutation == "type": answer["type"] = "noul"
    client, _, bedrock = live_client(payload)
    response = client.post("/rescue", json=RAIL | {"mode": "live"})
    assert response.status_code == 502
    assert isinstance(response.json()["detail"], str)
    assert bedrock.requests == []


@pytest.mark.parametrize("field", ["confidence", "probabilities"])
def test_enormous_provider_numbers_return_structured_error_before_tool_execution(field, monkeypatch):
    payload = wire()
    answer = payload["answers"]["next_tool"]
    if field == "confidence":
        answer["confidence"] = 10 ** 400
    else:
        answer["probabilities"]["find_transport"] = 10 ** 400
    tool_calls = []

    def unexpected_tool(*args):
        tool_calls.append(args)
        raise AssertionError("Malformed provider data must not execute a recovery tool")

    monkeypatch.setattr("backend.app.run_tool", unexpected_tool)
    client, requests, bedrock = live_client(payload)
    response = client.post("/rescue", json=RAIL | {"mode": "live"})
    assert response.status_code == 502
    assert isinstance(response.json()["detail"], str)
    assert "invalid numeric confidence or probability" in response.json()["detail"]
    assert len(requests) == 1  # Exercised the real Decider HTTP adapter.
    assert tool_calls == []
    assert bedrock.requests == []


def test_decider_http_failure_does_not_leak_response_or_fallback():
    client, _, bedrock = live_client({"secret": "do-not-leak"}, http_status=503)
    response = client.post("/rescue", json=RAIL | {"mode": "live"})
    assert response.status_code == 502
    assert "do-not-leak" not in response.text
    assert bedrock.requests == []


def test_bedrock_failure_is_clean_error_without_demo_fallback():
    client, _, _ = live_client(bedrock=FakeBedrock(error=RuntimeError("secret-credential")))
    response = client.post("/rescue", json=RAIL | {"mode": "live"})
    assert response.status_code == 502
    assert "secret-credential" not in response.text


def test_live_no_options_is_grounded_in_empty_evidence():
    client, _, bedrock = live_client()
    body = client.post("/rescue", json=RAIL | {"mode": "live", "budget": 1}).json()
    assert body["status"] == "no_options"
    assert body["options"] == []
    assert json.loads(bedrock.requests[0]["messages"][0]["content"][0]["text"].split("\nTool evidence:\n", 1)[1])["options"] == []


@pytest.mark.parametrize("changes", [{"budget": -1}, {"budget": True}, {"budget": "3000"}, {"current_time": "24:00"}, {"arrive_by": "12:00"}, {"mode": "pretend"}])
def test_bad_input_returns_string_detail(changes):
    response = TestClient(create_app()).post("/rescue", json=RAIL | changes)
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)


def test_live_configuration_is_required_and_health_does_not_claim_connectivity():
    client = TestClient(create_app(settings=Settings()))
    health = client.get("/health").json()
    assert health["status"] == "ok" and not health["live_configured"]
    assert health["inventory"] == "fixtures"
    assert client.post("/rescue", json=RAIL | {"mode": "live"}).status_code == 503


@pytest.mark.parametrize("trip,choice", [(FLIGHT, "find_stay"), (WEATHER, "check_disruptions")])
def test_other_live_scenarios_keep_fixture_provenance(trip, choice):
    client, _, _ = live_client(wire(choice=choice))
    response = client.post("/rescue", json=trip | {"mode": "live"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready" and body["selected_tool"] == choice
    assert body["provenance"]["inventory"] == "fictional fixtures"
    assert body["provenance"]["explanation"] == "Amazon Bedrock Converse live"


def test_explicit_clarify_abstains_even_at_high_confidence():
    client, _, bedrock = live_client(wire(choice="clarify"))
    body = client.post("/rescue", json=RAIL | {"mode": "live"}).json()
    assert body["status"] == "clarify" and not body["options"]
    assert not bedrock.requests


@pytest.mark.parametrize("changes", [{"budget": 100}, {"arrive_by": "19:00"}, {"current_time": "19:00"}])
def test_stays_enforce_price_and_checkin_schedule(changes):
    body = TestClient(create_app()).post("/rescue", json=FLIGHT | changes).json()
    assert body["status"] == "no_options"
    assert body["options"] == []


def test_flight_transport_request_does_not_fabricate_same_evening_connection():
    body = TestClient(create_app()).post("/rescue", json=FLIGHT | {"message": "I missed my flight. Find transport to Bengaluru."}).json()
    assert body["selected_tool"] == "find_transport"
    assert body["status"] == "no_options"


def test_case_and_outer_whitespace_normalization_preserves_supported_route():
    body = TestClient(create_app()).post("/rescue", json=RAIL | {"origin": " VARKALA ", "destination": " kochi "}).json()
    assert body["status"] == "ready"


def test_decider_timeout_has_safe_error():
    def timeout(request):
        raise httpx.ReadTimeout("private endpoint data", request=request)
    provider = DeciderClient("http://decider.test", client=httpx.Client(transport=httpx.MockTransport(timeout)))
    with pytest.raises(DecisionError, match="timed out") as failure:
        provider.select({"message": "help"})
    assert "private endpoint" not in str(failure.value)


def test_non_json_decider_response_has_safe_error():
    provider = DeciderClient("http://decider.test", client=httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, text="private invalid body"))))
    with pytest.raises(DecisionError, match="invalid JSON"):
        provider.select({})


@pytest.mark.parametrize("response", [{"output": {}}, {"output": {"message": {"content": [{"text": " "}]}}}])
def test_malformed_bedrock_content_is_not_a_success(response):
    client, _, _ = live_client(bedrock=FakeBedrock(response=response))
    result = client.post("/rescue", json=RAIL | {"mode": "live"})
    assert result.status_code == 502


@pytest.mark.parametrize("bad_probabilities", [
    {"find_transport": 0.5, "find_stay": 0.1, "check_disruptions": 0.1, "clarify": 0.1},
    {"find_transport": 0.1, "find_stay": 0.7, "check_disruptions": 0.1, "clarify": 0.1},
    {"find_transport": True, "find_stay": 0, "check_disruptions": 0, "clarify": 0},
])
def test_invalid_or_inconsistent_distributions_are_rejected(bad_probabilities):
    payload = wire()
    payload["answers"]["next_tool"]["probabilities"] = bad_probabilities
    with pytest.raises(DecisionError):
        validate_answer(payload)


def test_recipe_supports_another_domains_named_tools():
    criteria = {"search": "Find a document", "clarify": "Ask for document context"}
    payload = {"model": "test", "answers": {"next_tool": {"type": "choice", "choice": "search", "confidence": 0.9, "probabilities": {"search": 0.95, "clarify": 0.05}}}}
    decision = validate_answer(payload, criteria)
    assert decision.choice == "search"


@pytest.mark.parametrize("value", [-1, 2, float("nan"), float("inf")])
def test_invalid_confidence_threshold_is_rejected(value):
    with pytest.raises(ValueError):
        Settings(confidence_threshold=value)


def test_missing_required_fields_still_use_string_error_contract():
    response = TestClient(create_app()).post("/rescue", json={"mode": "demo"})
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)


def test_short_term_bedrock_key_enables_configuration_without_exposing_key(monkeypatch):
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "test-private-bearer")
    monkeypatch.setenv("STRANDS_DECIDER_URL", "http://127.0.0.1:8099")
    monkeypatch.setenv("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")
    settings = Settings.from_env()
    response = TestClient(create_app(settings=settings)).get("/health")
    assert response.json()["live_configured"] is True
    assert "test-private-bearer" not in response.text
    assert "test-private-bearer" not in repr(settings)


def test_explanation_cannot_claim_no_fixtures_when_tool_returned_options():
    bedrock = FakeBedrock(response={"output": {"message": {"content": [{"text": "None of the fixtures fit the specified constraints."}]}}})
    client, _, _ = live_client(bedrock=bedrock)
    response = client.post("/rescue", json=RAIL | {"mode": "live"})
    assert response.status_code == 502
