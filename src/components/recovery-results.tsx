import { ArrowRight, BedDouble, BusFront, Check, CircleHelp, CloudRain, Compass, MapPin, TrainFront, CarFront } from "lucide-react";
import { money } from "@/lib/scenarios";
import type { RecoveryOption, RescueResult } from "@/lib/types";

const icons = {bus:BusFront, train:TrainFront, taxi:CarFront, stay:BedDouble, advisory:CloudRain};
export function RecoveryResults({result,busy,selected,onSelect}: {result:RescueResult|null;busy:boolean;selected:string|null;onSelect:(id:string)=>void}) {
  return <section className="results-panel" aria-labelledby="results-title" aria-busy={busy}>
    <div className="section-heading"><div><span className="eyebrow">A WAY FORWARD</span><h2 id="results-title">Your recovery plan</h2></div>{result && <span className="count-pill">{result.options.length} {result.options.length === 1 ? "option" : "options"}</span>}</div>
    {!result ? <div className="results-empty"><span className={`empty-compass ${busy ? "is-spinning" : ""}`}><Compass size={35} strokeWidth={1.3}/></span><h3>{busy ? "Finding your next move…" : "Let’s find your next move."}</h3><p>{busy ? "Choosing a tool and checking the options against your trip." : "Tell us what changed. We’ll work with your budget and timing to find a way forward."}</p><span className="empty-hint"><MapPin size={13}/> Start with one of the three scenarios</span></div> : <>
      <div className={`result-summary ${result.status !== "ready" ? "needs-attention" : ""}`} role="status"><span className="summary-icon">{result.status === "ready" ? <Check size={18}/> : <CircleHelp size={18}/>}</span><div><h3>{result.status === "ready" ? "Here’s what you can do next." : result.status === "clarify" ? "A little more detail will help." : "No matching options this time."}</h3><p>{result.summary}</p>{result.question && <p className="clarification">{result.question}</p>}</div></div>
      <div className="option-list">{result.options.map(option => <OptionCard key={option.id} option={option} selected={selected === option.id} onSelect={()=>onSelect(option.id)}/>)}</div>
      {result.options.length === 0 && <p className="no-options-hint">Update your trip details above and run recovery again. Demo inventory covers only the preset locations.</p>}
      <p className="inventory-note">All travel options and disruption reports are fictional demo data. No reservation is made.</p>
    </>}
  </section>;
}
function OptionCard({option,selected,onSelect}: {option:RecoveryOption;selected:boolean;onSelect:()=>void}) {
  const Icon = icons[option.kind];
  return <article className={`option-card ${selected ? "option-selected" : ""}`}>
    <button className="option-select" onClick={onSelect} aria-expanded={selected} aria-controls={`steps-${option.id}`}>
      <span className="transport-icon"><Icon size={22}/></span><span className="option-main"><strong>{option.title}</strong><span>{option.subtitle}</span></span><span className="option-price">{option.cost === null ? "Advisory" : money(option.cost)}<small>{option.cost === null ? "Read report" : "Fixture price"}</small></span><ArrowRight size={17} className="option-arrow"/>
    </button>
    <div className="option-details">{option.departure && <span>{option.departure} → {option.arrival}</span>}{option.duration_minutes !== null && <span>{Math.floor(option.duration_minutes/60)}h {option.duration_minutes%60}m</span>}{option.tags.map(tag=><span className="option-tag" key={tag}>{tag}</span>)}</div>
    {selected && <div id={`steps-${option.id}`} className="option-steps"><span className="eyebrow">NEXT STEPS</span><ol>{option.steps.map((step,i)=><li key={i}>{step}</li>)}</ol></div>}
  </article>;
}
