import { ArrowUpRight, LocateFixed, Navigation, Route } from "lucide-react";
import type { RescueRequest, RescueResult } from "@/lib/types";
const mapLabel = (value: string) => value.length > 16 ? `${value.slice(0, 15)}…` : value;

export function RouteMap({request, result, busy}: {request:RescueRequest; result:RescueResult|null; busy:boolean}) {
  const isWeather = request.scenario === "weather";
  const isFlight = request.scenario === "flight";
  const canRecover = result?.status === "ready";
  return <section className={`map-panel ${busy ? "map-working" : ""}`} aria-label="Illustrative journey map">
    <div className="map-top"><span className="map-label"><Navigation size={13} /> SOUTH INDIA / JOURNEY VIEW</span><span className="map-scale">SCHEMATIC · NOT FOR NAVIGATION</span></div>
    <svg className="journey-map" viewBox="0 0 850 410" role="img" aria-label={`Illustrative map for ${request.origin} to ${request.destination}. It does not show verified travel routes.`}>
      <defs>
        <pattern id="map-grid" width="42" height="42" patternUnits="userSpaceOnUse"><path d="M42 0H0V42" fill="none" stroke="#b7cbd5" strokeWidth="0.6" opacity=".4" /></pattern>
        <pattern id="land-dots" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".65" fill="#c8d3ce" /></pattern>
        <filter id="label-shadow"><feDropShadow dx="0" dy="2" stdDeviation="5" floodColor="#183446" floodOpacity=".1" /></filter>
      </defs>
      <rect width="850" height="410" fill="#e7f0f5" />
      <rect width="850" height="410" fill="url(#map-grid)" />
      <path d="M315-30C340 10 305 45 348 80S366 133 398 172 390 218 429 248 439 286 467 323 479 376 531 440H900V-30Z" fill="#f1f4ec" stroke="#b9ced0" strokeWidth="2" />
      <path d="M315-30C340 10 305 45 348 80S366 133 398 172 390 218 429 248 439 286 467 323 479 376 531 440H900V-30Z" fill="url(#land-dots)" />
      <g fill="none" stroke="#d6e1d1" strokeWidth="1.2">
        <path d="M550-15Q485 85 550 118T590 230 662 300 680 420"/><path d="M578-15Q516 85 580 118T620 230 692 300 710 420"/><path d="M606-15Q547 85 610 118T650 230 722 300 740 420"/><path d="M634-15Q578 85 640 118T680 230 752 300 770 420"/><path d="M662-15Q609 85 670 118T710 230 782 300 800 420"/>
      </g>
      <path d="M402 0Q349 47 407 107T442 190 485 279 538 410" stroke="#fff" strokeWidth="7" fill="none" />
      <path d="M402 0Q349 47 407 107T442 190 485 279 538 410" stroke="#cbd2cd" strokeWidth="1" fill="none" />
      <path d="M370 120Q470 70 579 113T739 88M423 220Q550 210 610 253T830 220M475 320Q565 280 688 345" fill="none" stroke="#fff" strokeWidth="5" />
      <text x="116" y="230" className="sea-label" transform="rotate(-21 116 230)">L A C C A D I V E  S E A</text>
      <text x="655" y="190" className="terrain-label" transform="rotate(62 655 190)">WESTERN GHATS</text>
      <text x="530" y="235" className="region-label">K E R A L A</text>
      <g className="minor-city"><circle cx="417" cy="192" r="3"/><text x="433" y="196">Alappuzha</text><circle cx="465" cy="284" r="3"/><text x="480" y="288">Kollam</text><circle cx="544" cy="385" r="3"/><text x="560" y="389">Thiruvananthapuram</text></g>
      {isFlight ? <>
        <path d="M380 115Q540-30 736 53" fill="none" stroke="#c87354" strokeWidth="2" strokeDasharray="6 7" />
        <circle cx="736" cy="53" r="5" fill="#183446"/><text x="685" y="36" className="city-label">Bengaluru ↗</text>
        <circle cx="380" cy="115" r="27" className="location-halo"/>
      </> : <>
        <path d={isWeather ? "M580 105Q480 63 380 115" : "M500 330Q407 247 380 115"} fill="none" stroke="#c87354" strokeWidth="2.5" strokeDasharray="5 7" />
        {canRecover && result.selected_tool === "find_transport" && <path d="M500 330C610 248 490 95 380 115" fill="none" stroke="#117a77" strokeWidth="4" className="recovery-route" />}
      </>}
      <g filter="url(#label-shadow)"><rect x="220" y="89" width="133" height="51" rx="8" fill="white"/><text x="235" y="109" className="pin-meta">{isFlight ? "YOU ARE HERE" : "DESTINATION"}</text><text x="235" y="128" className="city-label">{mapLabel(isFlight ? request.origin : request.destination)}</text></g>
      <circle cx="380" cy="115" r="10" fill="white" stroke="#117a77" strokeWidth="3"/><circle cx="380" cy="115" r="4" fill="#117a77"/>
      {!isFlight && <g>
        <circle cx={isWeather ? 580 : 500} cy={isWeather ? 105 : 330} r="19" className="location-halo" />
        <circle cx={isWeather ? 580 : 500} cy={isWeather ? 105 : 330} r="7" fill="#183446" stroke="white" strokeWidth="3" />
        <g filter="url(#label-shadow)" transform={isWeather ? "translate(603 82)" : "translate(532 309)"}><rect width="138" height="51" rx="8" fill="white"/><text x="14" y="20" className="pin-meta">YOU ARE HERE</text><text x="14" y="39" className="city-label">{mapLabel(request.origin || "Your location")}</text></g>
      </g>}
      <g transform={isWeather ? "translate(481 84)" : isFlight ? "translate(548 34)" : "translate(423 222)"}><circle r="13" fill="#fff" stroke="#e9c1b0"/><path d="m-4-4 8 8m0-8-8 8" stroke="#bf5936" strokeWidth="2" strokeLinecap="round"/></g>
      <g transform="translate(794 334)" fill="none" stroke="#667d89"><path d="M0 30V0m-5 10L0 0l5 10"/><text x="-4" y="-9" className="pin-meta" stroke="none">N</text></g>
    </svg>
    <div className="map-bottom"><div className="map-key"><span><i className="key-line disrupted"/> Disrupted journey</span>{canRecover && result.selected_tool === "find_transport" && <span><i className="key-line"/> Recovery illustration</span>}</div><span className="map-credit">Illustrative map</span></div>
    <div className="journey-strip"><span className="journey-strip-icon"><Route size={21}/></span><div className="journey-places"><span className="eyebrow">YOUR JOURNEY</span><p><span>{request.origin || "Origin"}</span><ArrowUpRight size={18}/><span>{request.destination || "Destination"}</span></p></div><span className="journey-time"><LocateFixed size={14}/>{request.current_time} IST <small>Scenario time</small></span></div>
  </section>;
}
