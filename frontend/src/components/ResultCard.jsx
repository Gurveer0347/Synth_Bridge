export function ResultCard({ result, onReset }) {
  if (!result) return null;

  const success = result.success;
  return (
    <section className={`result-card ${success ? "is-success" : "is-error"}`}>
      <div className="result-status">{success ? "OK" : "!"}</div>
      <div>
        <h3>{success ? "Bridge delivered successfully" : "ALI needs attention"}</h3>
        <p>
          {success
            ? "The sandbox executed the generated bridge and confirmed delivery."
            : result.error || "The sandbox returned a failure state."}
        </p>
        <small>
          Attempts: {result.attemptsCount}
          {result.fromFallback ? " | Local visual demo fallback" : " | Flask backend response"}
        </small>
      </div>
      <button className="secondary-button" type="button" onClick={onReset}>
        Run Again
      </button>
    </section>
  );
}
