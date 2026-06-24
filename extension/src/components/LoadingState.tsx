interface LoadingStateProps {
  runId: string | null;
}

export function LoadingState({ runId }: LoadingStateProps) {
  return (
    <section className="status-card panel-loading">
      <div className="spinner" aria-hidden="true" />
      <div>
        <p className="overline">Processing</p>
        <h2>Analyzing brief…</h2>
        <p className="helper-text">Validating structured output from the provider.</p>
        {runId ? <p className="run-id">{runId}</p> : null}
      </div>
    </section>
  );
}
