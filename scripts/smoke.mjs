import assert from "node:assert/strict";
import { scenarios } from "../src/lib/scenarios.ts";

const base = process.env.TRIP_RESCUE_TEST_URL || "http://127.0.0.1:3100";
async function post(request, origin = new URL(base).origin) {
  const response = await fetch(`${base}/api/rescue`, {
    method:"POST",headers:{"Content-Type":"application/json",Origin:origin},
    body:JSON.stringify(request),signal:AbortSignal.timeout(10000),
  });
  return {status:response.status,body:await response.json()};
}
for (const [id,tool] of [["rail","find_transport"],["flight","find_stay"],["weather","check_disruptions"]]) {
  const {status,body} = await post(scenarios[id].request);
  assert.equal(status,200);assert.equal(body.status,"ready");assert.equal(body.selected_tool,tool);
  assert.equal(body.decision.confidence,null);assert.equal(body.decision.latency_ms,null);
  assert.equal(body.provenance.inventory,"fictional fixtures");
  assert.ok(body.options.length > 0);
  console.log(`PASS ${id}: ${tool}, ${body.options.length} fixture options`);
}
const poor = await post({...scenarios.rail.request,budget:100});
assert.equal(poor.status,200);assert.equal(poor.body.status,"no_options");assert.deepEqual(poor.body.options,[]);
console.log("PASS budget cannot produce unaffordable options");
const missing = await post({...scenarios.rail.request,origin:""});
assert.equal(missing.body.status,"clarify");assert.ok(!missing.body.trace.some(step=>step.stage === "tool"));
console.log("PASS missing origin pauses before tool execution");
const wrongOrigin = await post(scenarios.rail.request,"https://unrelated.example");
assert.equal(wrongOrigin.status,403);assert.equal(typeof wrongOrigin.body.detail,"string");
console.log("PASS cross-origin request rejected; same-origin scenarios passed");
const badTime = await post({...scenarios.rail.request,arrive_by:"12:00"});
assert.equal(badTime.status,422);assert.equal(typeof badTime.body.detail,"string");
console.log("PASS impossible same-day time window has a readable validation error");
