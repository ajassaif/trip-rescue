"use client";

import { useState } from "react";
import Link from "next/link";
import { Download, LifeBuoy } from "lucide-react";
import { RecoveryResults } from "./recovery-results";
import { DecisionLog } from "./decision-log";
import type { RescueRequest, RescueResult } from "@/lib/types";
import rail from "../../docs/evidence/aws/rail.json";
import flight from "../../docs/evidence/aws/flight.json";
import weather from "../../docs/evidence/aws/weather.json";
import ambiguous from "../../docs/evidence/aws/ambiguous.json";
import styles from "./evidence.module.css";

type Run = { recorded_at_utc: string; request: RescueRequest; result: RescueResult };
const runs = { rail, flight, weather, ambiguous } as Record<string, Run>;
const labels = { rail: "Cancelled train", flight: "Missed flight", weather: "Monsoon disruption", ambiguous: "Uncertain next step" };

export function EvidenceDesk() {
  const [active, setActive] = useState<keyof typeof labels>("rail");
  const [selected, setSelected] = useState<string | null>(null);
  const run = runs[active];
  function download() {
    const url = URL.createObjectURL(new Blob([JSON.stringify(run, null, 2)], { type: "application/json" }));
    const anchor = document.createElement("a");
    anchor.href = url; anchor.download = `trip-rescue-aws-${active}.json`; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return <>
    <header className="site-header">
      <Link className="brand" href="/" aria-label="Trip Rescue home"><span className="brand-mark"><LifeBuoy size={24}/></span><span>trip<span className="brand-light">rescue</span>.</span></Link>
      <nav aria-label="Main navigation"><Link href="/">Recovery desk</Link><a href="https://github.com/ajassaif/trip-rescue">Source &amp; recipe</a></nav>
      <span className={styles.badge}>RECORDED AWS RUNS</span>
    </header>
    <main className={styles.shell}>
      <section className={styles.intro}>
        <span className="eyebrow">VERIFIED ON AWS · 18 OCTOBER 2026</span>
        <h1>One next move.<br/><span>Four real model runs.</span></h1>
        <p>Decider chose. The agent checked. Bedrock explained.</p>
        <div className={styles.notice}>Saved AWS responses, replayed for inspection. Switching examples makes no model calls. All travel inventory is fictional.</div>
      </section>
      <div className={styles.tabs} role="group" aria-label="Recorded scenarios">
        {Object.entries(labels).map(([key, label]) => <button key={key} aria-pressed={active === key} onClick={() => { setActive(key as keyof typeof labels); setSelected(null); }}>{label}</button>)}
      </div>
      <section className={styles.request} aria-label="Recorded request">
        <div><span className="eyebrow">THE TRAVELER ASKED</span><p>{run.request.message}</p></div>
        <dl><div><dt>Route</dt><dd>{run.request.origin} → {run.request.destination}</dd></div><div><dt>Budget</dt><dd>₹{run.request.budget.toLocaleString("en-IN")}</dd></div><div><dt>Deadline</dt><dd>{run.request.arrive_by} IST</dd></div></dl>
      </section>
      <div className={styles.grid} key={active}>
        <RecoveryResults result={run.result} busy={false} selected={selected} onSelect={id => setSelected(selected === id ? null : id)}/>
        <DecisionLog result={run.result} busy={false} onExport={download}/>
      </div>
      <section className={styles.provenance}>
        <div><span className="eyebrow">WHERE THIS RAN</span><h2>AWS EC2 + Amazon Bedrock</h2><p>c7i.2xlarge · 8 vCPU · 16 GiB · us-east-1<br/>Strands Decider 2B, CPU · Nova Micro via an instance role</p></div>
        <div><span className="eyebrow">WHAT THIS ESTABLISHES</span><p>Three tool choices and one abstention were observed. These examples are not an accuracy or performance benchmark. The experimental confidence gate is 0.80.</p><button className="text-button" onClick={download}><Download size={15}/> Download the original response</button></div>
      </section>
    </main>
  </>;
}
