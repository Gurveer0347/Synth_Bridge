import { useEffect, useRef, useState } from "react";
import gsap from "gsap";

import { runAliBridge } from "../api/aliClient";
import { getStageIndex } from "../data/pipeline";
import { CodeWindow } from "./CodeWindow";
import { NetworkCanvas } from "./NetworkCanvas";
import { PipelineTimeline } from "./PipelineTimeline";
import { ResultCard } from "./ResultCard";
import { UploadZone } from "./UploadZone";

const DEFAULT_INSTRUCTION = "When a new lead is added in HubSpot, send an alert to Discord #sales-alerts";

export function ToolPage() {
  const [toolA, setToolA] = useState(null);
  const [toolB, setToolB] = useState(null);
  const [instruction, setInstruction] = useState(DEFAULT_INSTRUCTION);
  const [activeIndex, setActiveIndex] = useState(0);
  const [status, setStatus] = useState("idle");
  const [result, setResult] = useState(null);
  const surfaceRef = useRef(null);

  const ready = Boolean(toolA && toolB && instruction.trim());

  useEffect(() => {
    if (!surfaceRef.current) return undefined;
    const context = gsap.context(() => {
      gsap.from(".tool-header, .upload-zone, .instruction-box, .run-row", {
        y: 26,
        autoAlpha: 0,
        stagger: 0.06,
        duration: 0.65,
        ease: "power3.out",
      });
    }, surfaceRef);
    return () => context.revert();
  }, []);

  const run = async () => {
    if (!ready || status === "running") return;
    setStatus("running");
    setResult(null);
    setActiveIndex(0);

    const stageTimer = window.setInterval(() => {
      setActiveIndex((index) => Math.min(index + 1, 4));
    }, 650);

    const response = await runAliBridge();
    window.clearInterval(stageTimer);
    setActiveIndex(getStageIndex(response.stage));
    setResult(response);
    setStatus(response.success ? "success" : "error");
  };

  const reset = () => {
    setToolA(null);
    setToolB(null);
    setInstruction(DEFAULT_INSTRUCTION);
    setActiveIndex(0);
    setStatus("idle");
    setResult(null);
  };

  const loadDemoDocs = () => {
    setToolA({ name: "HubSpot_API_Docs.md" });
    setToolB({ name: "Discord_Webhook_Docs.md" });
    setInstruction(DEFAULT_INSTRUCTION);
  };

  return (
    <main className="page tool-page" ref={surfaceRef}>
      <NetworkCanvas density={56} />
      <div className="container">
        <header className="tool-header">
          <div>
            <p className="section-kicker" style={{ textAlign: "left" }}>
              ALI Tool Interface
            </p>
            <h1 className="tool-title">Generate the bridge. Watch it heal.</h1>
            <p className="tool-lede">
              Upload two API docs, describe the workflow, and let ALI generate, execute, and repair the Python
              integration through Gurveer's sandbox.
            </p>
          </div>
          <div className="user-chip">Savneet Kaur</div>
        </header>

        <div className="tool-surface">
          <div className="upload-grid">
            <UploadZone
              label="Tool A - API Documentation"
              subtext="Drop your .txt, .md, or .pdf file here"
              file={toolA}
              onFile={setToolA}
            />
            <UploadZone
              label="Tool B - API Documentation"
              subtext="Drop your .txt, .md, or .pdf file here"
              file={toolB}
              onFile={setToolB}
            />
          </div>

          <div className="instruction-box">
            <label htmlFor="instruction">What do you want ALI to do?</label>
            <textarea id="instruction" value={instruction} onChange={(event) => setInstruction(event.target.value)} />
          </div>

          <div className="run-row">
            <button className="primary-button pulse-button" type="button" disabled={!ready || status === "running"} onClick={run}>
              {status === "running" ? <span className="spinner" aria-label="Running" /> : "Run ALI"}
            </button>
            <button className="secondary-button" type="button" onClick={loadDemoDocs}>
              Load Demo Docs
            </button>
            <button className="secondary-button" type="button" onClick={reset}>
              Reset
            </button>
          </div>

          {status !== "idle" && <PipelineTimeline activeIndex={activeIndex} status={status} />}
          {result?.finalCode && <CodeWindow key={result.finalCode} code={result.finalCode} />}
          <ResultCard result={result} onReset={reset} />
        </div>
      </div>
    </main>
  );
}
