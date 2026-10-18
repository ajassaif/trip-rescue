import { agentRequest } from "@/lib/proxy";
export async function GET() { return agentRequest("/health"); }
