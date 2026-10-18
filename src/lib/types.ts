export type Mode = "demo" | "live";
export type ScenarioId = "rail" | "flight" | "weather";
export type RescueRequest = {
  mode: Mode; scenario: ScenarioId; message: string; origin: string; destination: string;
  budget: number; current_time: string; arrive_by: string;
};
export type RecoveryOption = {
  id: string; kind: "bus" | "train" | "taxi" | "stay" | "advisory";
  title: string; subtitle: string; departure: string | null; arrival: string | null;
  duration_minutes: number | null; cost: number | null; tags: string[]; steps: string[];
};
export type RescueResult = {
  id: string; mode: Mode; status: "ready" | "clarify" | "no_options"; summary: string;
  question: string | null; selected_tool: string;
  decision: {choice: string; confidence: number | null; latency_ms: number | null; source: string; model: string | null; probabilities: Record<string, number>};
  options: RecoveryOption[];
  trace: {stage: string; title: string; detail: string; duration_ms: number | null}[];
  provenance: {decision: string; explanation: string; inventory: string}; total_ms: number;
};
export type Health = {status: string; live_configured: boolean; missing: string[]; inventory: string};
