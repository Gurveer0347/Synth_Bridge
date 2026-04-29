import { PIPELINE_STAGES } from "../data/pipeline";

export function PipelineTimeline({ activeIndex, status }) {
  return (
    <section className="timeline-card" aria-label="ALI pipeline progress">
      <div className="timeline">
        {PIPELINE_STAGES.map((stage, index) => {
          const isComplete = status !== "idle" && index < activeIndex;
          const isActive = status === "running" && index === activeIndex;
          const isFinalComplete = status === "success" && index <= activeIndex;
          const isError = status === "error" && index === activeIndex;
          return (
            <article
              className={`timeline-step ${isComplete || isFinalComplete ? "is-complete" : ""} ${
                isActive ? "is-active" : ""
              } ${isError ? "is-error" : ""}`}
              key={stage.key}
            >
              <div className="timeline-number">
                {isComplete || isFinalComplete ? "✓" : isError ? "!" : String(index + 1).padStart(2, "0")}
              </div>
              <div className="timeline-body">
                <h3>{stage.title}</h3>
                <p>{stage.description}</p>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
