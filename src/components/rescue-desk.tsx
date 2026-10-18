"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import Link from "next/link";
import { ArrowRight, ArrowUpRight, Check, ChevronDown, CircleHelp, CloudRain, Code2, Download, ExternalLink, FlaskConical, GitBranch, LifeBuoy, MapPin, Plane, Play, Radio, RotateCcw, TrainFront, X } from "lucide-react";
import { RouteMap } from "./route-map";
import { DecisionLog } from "./decision-log";
import { RecoveryResults } from "./recovery-results";
import { scenarios } from "@/lib/scenarios";
import type { Health, RescueRequest, RescueResult, ScenarioId } from "@/lib/types";

const scenarioIcons = {rail:TrainFront, flight:Plane, weather:CloudRain};
async function fetchHealth(): Promise<Health> {
  const response = await fetch("/api/health", {signal:AbortSignal.timeout(7000)});
  if (!response.ok) throw new Error("Unavailable");
  return response.json();
}

export function RescueDesk() {
  const [form,setForm] = useState<RescueRequest>({...scenarios.rail.request});
  const [result,setResult] = useState<RescueResult|null>(null);
  const [selected,setSelected] = useState<string|null>(null);
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState("");
  const [health,setHealth] = useState<Health|null>(null);
  const [healthError,setHealthError] = useState(false);
  const [dialogContent,setDialogContent] = useState<"how"|"pattern"|"connection">("how");
  const dialog = useRef<HTMLDialogElement>(null);
  const controller = useRef<AbortController|null>(null);

  async function refreshHealth() {
    try {
      setHealth(await fetchHealth()); setHealthError(false);
    } catch {setHealth(null);setHealthError(true);}
  }
  useEffect(()=>{
    let active = true;
    fetchHealth().then(data=>{if(active) {setHealth(data);setHealthError(false);}}).catch(()=>{if(active) setHealthError(true);});
    return ()=>{active=false;controller.current?.abort();};
  },[]);
  function openDialog(content: "how"|"pattern"|"connection") {setDialogContent(content);dialog.current?.showModal();}
  function update<K extends keyof RescueRequest>(key:K,value:RescueRequest[K]) {
    setForm(current=>({...current,[key]:value}));setResult(null);setSelected(null);setError("");
  }
  function chooseScenario(id:ScenarioId) {
    setForm({...scenarios[id].request,mode:form.mode});setResult(null);setSelected(null);setError("");
  }
  async function runRecovery(event:FormEvent) {
    event.preventDefault();setBusy(true);setError("");setResult(null);setSelected(null);
    controller.current = new AbortController();
    const timeout = setTimeout(()=>controller.current?.abort(),185000);
    try {
      const response = await fetch("/api/rescue", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(form),signal:controller.current.signal});
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Check your trip details and try again. Your times must use the same scenario day.");
      setResult(data);setSelected(data.options[0]?.id || null);
    } catch (cause) {
      setError(cause instanceof Error && cause.name === "AbortError" ? "The recovery request timed out. Check the model services and try again." : cause instanceof Error ? cause.message : "Recovery could not finish. Please try again.");
    } finally {clearTimeout(timeout);setBusy(false);controller.current=null;}
  }
  function exportRun() {
    if (!result) return;
    const blob = new Blob([JSON.stringify({request:form,result},null,2)], {type:"application/json"});
    const url = URL.createObjectURL(blob);const anchor=document.createElement("a");
    anchor.href=url;anchor.download=`trip-rescue-${result.id}.json`;anchor.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }

  return <>
    <a className="skip-link" href="#trip-form">Skip to trip details</a>
    <header className="site-header"><Link className="brand" href="/" aria-label="Trip Rescue home"><span className="brand-mark"><LifeBuoy size={24} strokeWidth={2}/></span><span>trip<span className="brand-light">rescue</span><span className="brand-period">.</span></span></Link>
      <nav aria-label="Main navigation"><a className="nav-active" href="#trip-form">Recovery desk</a><button onClick={()=>openDialog("pattern")}>Decision pattern <ArrowUpRight size={12}/></button><button onClick={()=>openDialog("how")}>How it works</button></nav>
      <button className="connection-pill" onClick={()=>openDialog("connection")}><span className={`status-dot ${healthError ? "status-error" : ""}`}/>{healthError ? "Service offline" : form.mode === "live" ? "Live models" : "Demo workspace"}<ChevronDown size={12}/></button>
    </header>

    <main className="main-shell">
      <section className="intro"><div><div className="intro-eyebrow"><span className="intro-dash"/> A LITTLE HELP WHEN PLANS CHANGE</div><h1>Find your way <span>forward.</span></h1><p>Missed connections happen. Let’s make your next move a good one.</p></div><div className="intro-stamp"><LifeBuoy size={24} strokeWidth={1.3}/><span>BUILT FOR<br/><strong>THE UNEXPECTED</strong></span></div></section>

      <div className="workspace-bar"><div><span className="desk-dot"/> RECOVERY DESK <span className="workspace-divider">/</span><span className="workspace-name">Kerala & beyond</span></div><button className="text-button" onClick={exportRun} disabled={!result || busy}><Download size={14}/> Export run</button></div>
      <div className="workspace-grid">
        <aside className="trip-panel">
          <div className="section-heading"><div><span className="eyebrow">LET’S START HERE</span><h2>Your trip, right now.</h2></div><MapPin size={21} className="subtle-icon"/></div>
          <form id="trip-form" onSubmit={runRecovery}>
            <fieldset disabled={busy} className="form-fields"><legend className="sr-only">Trip details</legend>
              <label className="field-label">Try a disruption scenario</label>
              <div className="scenario-picker" role="group" aria-label="Disruption scenarios">{(Object.keys(scenarios) as ScenarioId[]).map(id=>{const Icon=scenarioIcons[id];return <button key={id} type="button" aria-pressed={form.scenario===id} className={form.scenario===id ? "scenario-active" : ""} onClick={()=>chooseScenario(id)}><Icon size={17}/><span>{scenarios[id].label}</span>{form.scenario===id ? <Check size={14}/> : <ArrowRight size={13}/>}</button>;})}</div>
              <label className="field-label" htmlFor="message">What happened?</label>
              <textarea id="message" required maxLength={2000} value={form.message} onChange={e=>update("message",e.target.value)} rows={5}/>
              <div className="location-fields"><div><label className="field-label" htmlFor="origin">You’re in</label><div className="input-with-icon"><span className="origin-dot"/><input id="origin" maxLength={100} value={form.origin} onChange={e=>update("origin",e.target.value)} placeholder="Your location" autoComplete="off"/></div></div><div><label className="field-label" htmlFor="destination">Heading to</label><div className="input-with-icon"><MapPin size={14}/><input id="destination" maxLength={100} value={form.destination} onChange={e=>update("destination",e.target.value)} placeholder="Your destination" autoComplete="off"/></div></div></div>
              <div className="constraint-fields"><div><label className="field-label" htmlFor="budget">Budget left</label><div className="input-with-icon"><span>₹</span><input type="number" id="budget" required min={0} max={1000000} step={1} value={Number.isNaN(form.budget) ? "" : form.budget} onChange={e=>update("budget",e.target.valueAsNumber)}/></div></div><div><label className="field-label" htmlFor="deadline">Arrive / check in by</label><input type="time" id="deadline" required value={form.arrive_by} onChange={e=>update("arrive_by",e.target.value)}/></div></div>
              <details className="scenario-clock"><summary>Scenario clock <span>{form.current_time} IST</span><ChevronDown size={13}/></summary><label className="field-label" htmlFor="current-time">Current time in the scenario</label><input id="current-time" type="time" required value={form.current_time} onChange={e=>update("current_time",e.target.value)}/><p>All times use the same fictional day in India. Overnight journeys aren’t included.</p></details>
              <div className="run-mode"><span>Run with</span><div className="mode-switch" role="group" aria-label="Execution mode"><button type="button" aria-pressed={form.mode==="demo"} onClick={()=>update("mode","demo")}>Demo</button><button type="button" aria-pressed={form.mode==="live"} disabled={!health?.live_configured} title={health?.live_configured ? "Use configured model services" : "Configure Decider and AWS on the server to enable live models"} onClick={()=>update("mode","live")}>Live models</button></div><button type="button" className="icon-button" aria-label="Model connection details" onClick={()=>openDialog("connection")}><CircleHelp size={15}/></button></div>
              <button type="submit" className="rescue-button" disabled={busy}>{busy ? <><span className="button-spinner"/> Working on your recovery</> : <>Find a way forward <ArrowRight size={19}/></>}</button>
              <p className="form-footnote"><FlaskConical size={12}/>{form.mode === "demo" ? "Demo rules · fictional travel data · no model calls" : "Live Decider + Bedrock · fictional travel data"}</p>
            </fieldset>
            {error && <div className="error-notice" role="alert"><strong>Recovery couldn’t finish</strong><p>{error}</p></div>}
            <span className="sr-only" role="status">{busy ? "Recovery in progress." : result ? `Recovery complete. ${result.options.length} options. ${result.status}.` : ""}</span>
          </form>
          <div className="care-note"><LifeBuoy size={19}/><p>A change of plans.<br/><strong>A fresh set of possibilities.</strong></p></div>
        </aside>

        <div className="journey-column"><RouteMap request={form} result={result} busy={busy}/><RecoveryResults result={result} busy={busy} selected={selected} onSelect={id=>setSelected(selected===id ? null : id)}/></div>
        <aside className="log-column"><DecisionLog result={result} busy={busy} onExport={exportRun}/><div className="experiment-note"><FlaskConical size={16}/><div><strong>A small decision. A useful difference.</strong><p>An experimental project for the AWS Agent Experience Hackathon.</p><button onClick={()=>openDialog("how")}>See how it works <ArrowUpRight size={13}/></button></div></div></aside>
      </div>
      <footer className="site-footer"><span><LifeBuoy size={14}/> A little resilience for the road.</span><div><span>Strands Decider 2B</span><span className="footer-plus">+</span><span>Amazon Bedrock</span><span className="footer-tag">EXPERIMENTAL</span></div></footer>
    </main>

    <dialog ref={dialog} className="info-dialog" onClick={e=>{if(e.target===dialog.current) dialog.current?.close();}} aria-labelledby="dialog-title">
      <div className="dialog-top"><span className="eyebrow">TRIP RESCUE / FIELD NOTES</span><button className="icon-button" onClick={()=>dialog.current?.close()} aria-label="Close dialog"><X size={20}/></button></div>
      {dialogContent === "how" ? <><h2 id="dialog-title">A useful next decision.</h2><p>Trip Rescue separates choosing the next action from explaining the result.</p><ol className="how-list"><li><GitBranch/><div><strong>Decide what to do.</strong><p>In live mode, Strands Decider 2B chooses transport, accommodation, disruption reports, or a clarifying question.</p></div></li><li><Check/><div><strong>Work with the evidence.</strong><p>The selected tool checks fixture data against your location, budget, and same-day timing. Low-confidence decisions pause for clarification.</p></div></li><li><Radio/><div><strong>Explain what comes next.</strong><p>Amazon Bedrock receives the tool evidence and writes a short recovery explanation. The trace keeps each step visible.</p></div></li></ol><p className="dialog-note">Demo mode uses deterministic routing and written summaries. Live mode uses real models with the same fictional travel inventory.</p></> : dialogContent === "pattern" ? <><h2 id="dialog-title">The tool-selection recipe.</h2><p>A typed choice sits directly before tool execution. Its output changes what the agent does next.</p><pre className="pattern-code">{JSON.stringify({type:"choice",instructions:"Which recovery tool should run next?",criteria:{find_transport:"Find an alternative way to reach the destination.",find_stay:"Find accommodation near the current location.",check_disruptions:"Read disruption reports before planning.",clarify:"Ask for information needed to proceed."}},null,2)}</pre><p>The backend recipe includes the full question, response validation, and confidence threshold. Find it in <code>patterns/tool_selection.py</code>.</p><p className="dialog-note">The initial 0.8 confidence threshold is a tunable experiment, not a guarantee of decision accuracy.</p><a className="text-link" href="https://github.com/strands-labs/strands-decider" target="_blank" rel="noreferrer">Read the official Decider documentation <ExternalLink size={14}/></a></> : <><h2 id="dialog-title">Model connections.</h2><div className="connection-state"><span className={`status-dot ${healthError ? "status-error" : ""}`}/><strong>{healthError ? "Backend unavailable" : health ? "Recovery backend is running" : "Checking backend…"}</strong></div><p>Demo mode works without cloud credentials. Live mode needs a running Decider server and Amazon Bedrock access.</p><div className="config-box"><Code2 size={18}/><div><strong>{health?.live_configured ? "Live configuration detected" : "Live setup required"}</strong><p>{health?.live_configured ? "Configuration is present. Connectivity and permissions are verified when you run a live recovery." : `Configure: ${health?.missing?.join(", ") || "STRANDS_DECIDER_URL, BEDROCK_MODEL_ID, and AWS credentials"}.`}</p></div></div><p>Keep credentials in the backend environment. The setup instructions are in the project README and AWS deployment guide.</p><button className="secondary-button" onClick={()=>void refreshHealth()}><RotateCcw size={15}/> Check connections again</button><p className="dialog-note">Travel inventory is fictional in both modes. A successful live run is required before claiming the model integration is verified.</p></>}
      <div className="dialog-bottom"><span><Play size={12}/> An experiment in getting unstuck.</span><button className="text-button" onClick={()=>dialog.current?.close()}>Back to the desk <ArrowRight size={14}/></button></div>
    </dialog>
  </>;
}
