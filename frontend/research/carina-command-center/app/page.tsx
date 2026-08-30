"use client";

import { useEffect, useMemo, useState } from "react";

const agents = [
  { name: "Carina", role: "Command center concept", status: "Demo idle", color: "violet", icon: "C" },
  { name: "Hermes", role: "Research & routing concept", status: "Demo queued", color: "cyan", icon: "H" },
  { name: "Clever AI", role: "Implementation concept", status: "Demo ready", color: "green", icon: "Cl" },
  { name: "ChatGPT", role: "Architecture concept", status: "Demo review", color: "amber", icon: "G" },
];

const projects = [
  { name: "Dino AI Operating System", detail: "Sample agent orchestration", progress: 78, agents: "C · H · Cl" },
  { name: "OpenClaw Integration", detail: "Sample tools and automations", progress: 62, agents: "H · Cl" },
  { name: "Workflow Learning Lab", detail: "Sample evaluation workflow", progress: 41, agents: "C · G" },
];

const ledger = [
  { label: "Agent handoff sample", time: "Demo event 01", amount: "+420", token: "POINTS" },
  { label: "Milestone sample", time: "Demo event 02", amount: "+1,250", token: "POINTS" },
  { label: "Review sample", time: "Demo event 03", amount: "+86", token: "POINTS" },
];

export default function Home() {
  const [active, setActive] = useState("Command Center");
  const [listening, setListening] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState("Carina");
  const [range, setRange] = useState("7D");
  const [message, setMessage] = useState("");
  const [notice, setNotice] = useState("Demo mode — no agents or external services are connected");
  const [engineRunning, setEngineRunning] = useState(false);
  const [whisperAlerts, setWhisperAlerts] = useState(true);
  const [engineEvents, setEngineEvents] = useState([
    { label: "Backend connection", detail: "Not configured", time: "Demo", tone: "amber" },
    { label: "Phone bridge", detail: "Not connected", time: "Demo", tone: "amber" },
    { label: "Interface preview", detail: "Local interactions available", time: "Demo", tone: "violet" },
  ]);
  const bars = useMemo(() => range === "24H" ? [18,24,22,31,29,44,51,48,66,61,78,83] : range === "30D" ? [22,32,28,38,45,42,58,54,63,72,69,84] : [28,34,31,48,42,56,62,55,68,74,71,86], [range]);

  const whisper = (frequency = 520) => {
    if (!whisperAlerts || typeof window === "undefined") return;
    const context = new window.AudioContext();
    const oscillator = context.createOscillator();
    const gain = context.createGain();
    oscillator.frequency.value = frequency;
    oscillator.type = "sine";
    gain.gain.setValueAtTime(0.0001, context.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.055, context.currentTime + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.22);
    oscillator.connect(gain).connect(context.destination);
    oscillator.start();
    oscillator.stop(context.currentTime + 0.24);
    oscillator.addEventListener("ended", () => void context.close());
  };

  const setEngine = (running: boolean) => {
    setEngineRunning(running);
    setListening(running);
    setNotice(running ? "Demo animation active — no agent action is running" : "Demo animation paused");
    setEngineEvents(events => [{ label: running ? "Demo wake control" : "Demo stop control", detail: running ? "Interface animation started · no systems dispatched" : "Interface animation paused", time: "Demo", tone: running ? "green" : "amber" }, ...events].slice(0, 3));
    whisper(running ? 660 : 360);
  };

  const sendMessage = () => {
    if (!message.trim()) return;
    const command = message.trim();
    const normalized = command.toLowerCase();
    if (normalized.includes("hey mami") && !normalized.includes("stop")) setEngine(true);
    else if (normalized.includes("mami stop") || normalized.includes("maya stop") || normalized === "stop") setEngine(false);
    else setNotice(`${selectedAgent} demo received: “${command}” · no agent action executed`);
    setMessage("");
  };

  useEffect(() => {
    if (!engineRunning) return;
    const timer = window.setInterval(() => {
      const load = (1.1 + Math.random() * 0.7).toFixed(2);
      setEngineEvents(events => [{ label: "Simulated orchestration", detail: `Interface-only sample · load ${load}`, time: "Demo", tone: "green" }, ...events].slice(0, 3));
    }, 8000);
    return () => window.clearInterval(timer);
  }, [engineRunning]);

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">C</span><div><strong>CARINA</strong><small>AI OPERATING SYSTEM</small></div></div>
        <nav aria-label="Primary navigation">
          {["Command Center", "Agents", "Projects", "Demo Ledger", "Automations"].map((item, i) => (
            <button key={item} className={active === item ? "nav-item active" : "nav-item"} onClick={() => setActive(item)}><span>{["⌁","◉","▦","◈","⌘"][i]}</span>{item}{item === "Agents" && <b>4</b>}</button>
          ))}
        </nav>
        <div className="side-bottom">
          <div className="connection"><div className="connection-row"><span className="claw">OC</span><div><strong>OpenClaw concept</strong><small><i className="offline" /> Not connected</small></div><button aria-label="OpenClaw demo settings">•••</button></div><div className="latency"><span>DEMO STATUS</span><strong>Simulated · local UI</strong></div></div>
          <button className="profile"><span>LF</span><div><strong>Leandro</strong><small>Owner workspace</small></div><b>⌄</b></button>
        </div>
      </aside>

      <section className="workspace">
        <header><div><p className="eyebrow">{active.toUpperCase()} <span>•</span> INTERACTIVE DEMO</p><h1>Good morning, Leandro.</h1><p>{notice}</p></div><div className="header-actions"><button aria-label="Demo notifications" className="icon-button">♢<i /></button><button className="new-task" onClick={() => { setActive("Command Center"); setNotice("Demo task ready — no agent will run"); }}>＋ New demo task</button></div></header>

        <aside className="demo-banner" aria-label="Demo environment notice"><div className="mode-state"><strong>HOSTED DEMO</strong><span>ACTIVE</span></div><p>This interface uses simulated agents, projects, events, and sample points. Nothing here represents a wallet, balance, phone bridge, or running automation.</p><div className="mode-state local"><strong>LOCAL LIVE</strong><span>NOT CONNECTED</span></div></aside>

        <div className="dashboard-grid">
          <section className="voice-panel panel">
            <div className="voice-copy"><span className="section-label">CARINA VOICE · DEMO CONTROL</span><h2>{listening ? "Listening animation…" : "Preview the voice experience"}</h2><p>{listening ? "This is a visual preview; no microphone audio is being captured." : "Use the control or type a command to preview the interface."}</p></div>
            <button className={listening ? "orb listening" : "orb"} onClick={() => setEngine(!engineRunning)} aria-label={listening ? "Stop demo listening animation" : "Preview demo listening animation"}><span className="orb-core">{listening ? "■" : "●"}</span><i className="ring one"/><i className="ring two"/></button>
            <div className="wave" aria-hidden="true">{Array.from({length: 25}).map((_,i)=><i key={i} style={{height: `${12 + ((i * 17) % 38)}px`}} />)}</div>
            <div className="command-box"><select value={selectedAgent} onChange={e=>setSelectedAgent(e.target.value)} aria-label="Choose agent">{agents.map(a=><option key={a.name}>{a.name}</option>)}</select><input value={message} onChange={e=>setMessage(e.target.value)} onKeyDown={e=>e.key === "Enter" && sendMessage()} placeholder={`Message ${selectedAgent}…`} aria-label={`Message ${selectedAgent}`} /><button onClick={sendMessage} aria-label="Send command">↑</button></div>
            <p className="secure-note">◉ Demo controls only · no microphone or agent backend connected</p>
          </section>

          <section className="token-panel panel">
            <div className="panel-head"><div><span className="section-label">DEMO ACTIVITY SCORE</span><h2>24,680 points</h2></div><span className="gain">↗ 12.4% sample</span></div>
            <p className="subvalue">Illustrative trend · not money or a balance</p>
            <div className="chart"><div className="chart-bars">{bars.map((h,i)=><i key={i} style={{height:`${h}%`}} className={i===bars.length-1 ? "last":""}/>)}</div><div className="chart-line" /></div>
            <div className="range">{["24H","7D","30D"].map(r=><button key={r} className={range===r?"selected":""} onClick={()=>setRange(r)}>{r}</button>)}</div>
            <div className="holdings"><div><span className="coin purple">R</span><p><strong>Research</strong><small>Sample category</small></p><b>12,840 pts</b></div><div><span className="coin blue">B</span><p><strong>Build</strong><small>Sample category</small></p><b>8,420 pts</b></div><div><span className="coin aqua">V</span><p><strong>Review</strong><small>Sample category</small></p><b>3,420 pts</b></div></div>
          </section>

          <section className="agents-panel panel"><div className="panel-title"><div><span className="section-label">AGENT CONCEPTS</span><h3>4 simulated roles</h3></div><button onClick={()=>setActive("Agents")}>Explore →</button></div><div className="agent-list">{agents.map(agent=><button key={agent.name} onClick={()=>{setSelectedAgent(agent.name);setNotice(`${agent.name} selected for this interface demo`);}} className={selectedAgent===agent.name?"agent selected":"agent"}><span className={`avatar ${agent.color}`}>{agent.icon}</span><p><strong>{agent.name}</strong><small>{agent.role}</small></p><em><i />{agent.status}</em></button>)}</div></section>

          <section className="projects-panel panel"><div className="panel-title"><div><span className="section-label">SAMPLE PROJECTS</span><h3>3 illustrative workflows</h3></div><button onClick={()=>setActive("Projects")}>Explore →</button></div><div className="project-list">{projects.map(p=><button key={p.name} onClick={()=>setNotice(`${p.name}: ${p.progress}% sample progress · demo data`)}><div className="project-row"><div><strong>{p.name}</strong><small>{p.detail}</small></div><span>{p.agents}</span></div><div className="progress"><i style={{width:`${p.progress}%`}}/></div><small>{p.progress}% sample progress</small></button>)}</div></section>

          <section className="ledger-panel panel"><div className="panel-title"><div><span className="section-label">SAMPLE ACTIVITY</span><h3>Demo points ledger</h3></div><button onClick={()=>setActive("Demo Ledger")}>Explore →</button></div>{ledger.map((item,i)=><div className="ledger-row" key={item.label}><span className={`ledger-icon l${i}`}>↗</span><p><strong>{item.label}</strong><small>{item.time}</small></p><b>{item.amount}<small>{item.token}</small></b></div>)}</section>
          <section className="engine-panel panel"><div className="engine-head"><div><span className="section-label">SYSTEMS ENGINE · INTERFACE DEMO</span><h3>Orchestration runtime preview</h3></div><button className={engineRunning ? "engine-toggle on" : "engine-toggle"} onClick={() => setEngine(!engineRunning)}><i />{engineRunning ? "Demo active" : "Demo paused"}</button></div><div className="engine-stats"><div><span>PREVIEW CONTEXT</span><strong>{engineRunning ? "Simulated Safari context" : "No runtime connected"}</strong></div><div><span>PHONE BRIDGE</span><strong>Not configured</strong></div><div><span>UPDATE CYCLE</span><strong>UI only · 8 seconds</strong></div></div><div className="event-stream">{engineEvents.map((event, index) => <div className="engine-event" key={`${event.label}-${index}`}><span className={`event-dot ${event.tone}`} /><p><strong>{event.label}</strong><small>{event.detail}</small></p><time>{event.time}</time></div>)}</div><div className="engine-controls"><button onClick={() => setEngine(true)} disabled={engineRunning}>Preview wake</button><button onClick={() => setEngine(false)} disabled={!engineRunning}>Preview stop</button><label><input type="checkbox" checked={whisperAlerts} onChange={event => setWhisperAlerts(event.target.checked)} /><span>Demo sound</span></label></div></section>
        </div>
      </section>
    </main>
  );
}
