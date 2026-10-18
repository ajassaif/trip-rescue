from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def minutes(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


class RescueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    mode: Literal["demo", "live"]
    scenario: Literal["rail", "flight", "weather"]
    message: str = Field(max_length=2000)
    origin: str = Field(max_length=100)
    destination: str = Field(max_length=100)
    budget: float = Field(ge=0, le=1000000, allow_inf_nan=False, strict=True)
    current_time: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    arrive_by: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")

    @field_validator("budget", mode="before")
    @classmethod
    def numeric_budget(cls, value):
        if type(value) not in (float, int):
            raise ValueError("budget must be a number")
        return value

    @model_validator(mode="after")
    def same_day_window(self):
        if minutes(self.arrive_by) <= minutes(self.current_time):
            raise ValueError("arrive_by must be after current_time on the same fictional IST day")
        return self


class Option(BaseModel):
    id: str
    kind: Literal["bus", "train", "taxi", "stay", "advisory"]
    title: str
    subtitle: str
    departure: str | None = None
    arrival: str | None = None
    duration_minutes: int | None = None
    cost: float | None = None
    tags: list[str]
    steps: list[str]


class DecisionView(BaseModel):
    choice: str
    confidence: float | None = None
    latency_ms: float | None = None
    source: str
    model: str | None = None
    probabilities: dict[str, float] = Field(default_factory=dict)


class TraceEvent(BaseModel):
    stage: str
    title: str
    detail: str
    duration_ms: float | None = None


class Provenance(BaseModel):
    decision: str
    explanation: str
    inventory: str = "fictional fixtures"


class RescueResponse(BaseModel):
    id: str
    mode: Literal["demo", "live"]
    status: Literal["ready", "clarify", "no_options"]
    summary: str
    question: str | None = None
    selected_tool: str
    decision: DecisionView
    options: list[Option]
    trace: list[TraceEvent]
    provenance: Provenance
    total_ms: float
