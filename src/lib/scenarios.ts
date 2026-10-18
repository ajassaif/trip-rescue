import type { RescueRequest, ScenarioId } from "./types";
export const scenarios: Record<ScenarioId, {label: string; short: string; description: string; request: RescueRequest}> = {
  rail: {
    label: "Cancelled train", short: "Rail cancellation", description: "Varkala → Kochi",
    request: {mode:"demo", scenario:"rail", origin:"Varkala", destination:"Kochi", budget:3000, current_time:"14:30", arrive_by:"21:00", message:"My train from Varkala to Kochi has been cancelled. I need to get there tonight, and I have ₹3,000 left. Can you find another way?"}
  },
  flight: {
    label: "Missed flight", short: "Missed departure", description: "An unexpected night in Kochi",
    request: {mode:"demo", scenario:"flight", origin:"Kochi", destination:"Bengaluru", budget:5000, current_time:"18:15", arrive_by:"23:30", message:"I missed the last flight from Kochi to Bengaluru. I need somewhere to stay in Kochi tonight, within ₹5,000, while I sort out tomorrow's travel."}
  },
  weather: {
    label: "Monsoon disruption", short: "Weather disruption", description: "Munnar → Kochi",
    request: {mode:"demo", scenario:"weather", origin:"Munnar", destination:"Kochi", budget:2500, current_time:"15:00", arrive_by:"22:00", message:"Heavy rain is disrupting my journey from Munnar to Kochi. Check the road disruption reports before we make a new plan. My budget is ₹2,500."}
  }
};
export const toolLabels: Record<string, string> = {find_transport:"Find alternative transport", find_stay:"Find a place to stay", check_disruptions:"Check local disruptions", clarify:"Ask a clarifying question"};
export const money = (value: number) => new Intl.NumberFormat("en-IN", {style:"currency", currency:"INR", maximumFractionDigits:0}).format(value);
