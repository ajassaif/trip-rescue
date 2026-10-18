import { ArrowDown, Check, ChevronDown, Code2, Cpu, Download, GitBranch } from "lucide-react";
import { toolLabels } from "@/lib/scenarios";
import type { RescueResult } from "@/lib/types";

export function DecisionLog({result, busy, onExport}: {result:RescueResult|null; busy:boolean; onExport:()=>void}) {
  return <section className="decision-panel" aria-labelledby="decision-title">
    <div className="section-heading"><div><span className="eyebrow">UNDER THE HOOD</span><h2 id="decision-title">The next move, explained.</h2></div><span className="square-icon"><GitBranch size={19}/></span></div>
    <p className="muted decision-intro">Follow the decision that shapes your recovery.</p>
    {!result ? <div className="empty-pipeline" aria-busy={busy}>
      <div><span className="pipeline-icon"><GitBranch size={18}/></span><strong>Choose a recovery tool</strong><span>Decider 2B in live mode</span></div>
      <ArrowDown size={15}/><div><span className="pipeline-icon"><Check size={18}/></span><strong>Check your constraints</strong><span>Budget, route, and time</span></div>
      <ArrowDown size={15}/><div><span className="pipeline-icon"><Cpu size={18}/></span><strong>Explain the way forward</strong><span>Amazon Bedrock in live mode</span></div>
      <p className="pipeline-note">{busy ? "Your request is being processed…" : "Run a recovery to inspect the actual trace."}</p>
    </div> : <>
      <div className="chosen-tool"><span className="eyebrow">SELECTED TOOL</span><strong>{toolLabels[result.selected_tool] || result.selected_tool}</strong><code>{result.selected_tool}</code></div>
      <div className="decision-metrics"><div><span>Confidence</span><strong>{result.decision.confidence === null ? "—" : `${Math.round(result.decision.confidence * 100)}%`}</strong></div><div><span>Decision latency</span><strong>{result.decision.latency_ms === null ? "—" : `${Math.round(result.decision.latency_ms)} ms`}</strong></div></div>
      {result.mode === "demo" && <p className="metric-note">Demo rules · no model confidence or inference measurement.</p>}
      <ol className="trace-list">{result.trace.map((step, index) => <li key={`${step.stage}-${index}`}><span className="trace-index">{index + 1}</span><div><strong>{step.title}</strong><p>{step.detail}</p></div></li>)}</ol>
      <details className="raw-trace"><summary><Code2 size={15}/> Inspect decision JSON <ChevronDown size={14}/></summary><pre>{JSON.stringify(result.decision, null, 2)}</pre></details>
      <button className="text-button export-button" onClick={onExport}><Download size={15}/> Download run evidence</button>
    </>}
    <div className="pattern-footer"><GitBranch size={14}/><span>Reusable pattern: <strong>tool selection</strong></span></div>
  </section>;
}
