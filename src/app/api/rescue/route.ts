import { agentRequest } from "@/lib/proxy";
export async function POST(request: Request) {
  const origin = request.headers.get("origin");
  if (origin) {
    try {
      // Next may normalize request.url to localhost behind the development proxy.
      // The incoming Host is the browser-facing authority, including its port.
      if (new URL(origin).host !== request.headers.get("host")) {
        return Response.json({detail:"Requests must come from this application."}, {status:403});
      }
    } catch {
      return Response.json({detail:"Invalid request origin."}, {status:403});
    }
  }
  const body = await request.text();
  if (body.length > 12000) return Response.json({detail:"Please shorten your request."}, {status:413});
  try { JSON.parse(body); } catch { return Response.json({detail:"Send a valid JSON request."}, {status:400}); }
  return agentRequest("/rescue", body);
}
