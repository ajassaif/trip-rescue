const base = () => process.env.AGENT_API_URL || "http://127.0.0.1:8100";
export async function agentRequest(path: string, body?: string) {
  try {
    const response = await fetch(`${base()}${path}`, {
      method: body === undefined ? "GET" : "POST",
      headers: {"Content-Type":"application/json"}, body,
      signal: AbortSignal.timeout(body === undefined ? 5000 : 180000), cache:"no-store",
    });
    const data = await response.json();
    return Response.json(data, {status: response.status});
  } catch {
    return Response.json({detail:"The recovery service is unavailable or timed out. Start the Python backend, then try again."}, {status:503});
  }
}
