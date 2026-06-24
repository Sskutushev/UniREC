interface LoadingStateProps {
  runId: string | null;
}

export function LoadingState({ runId }: LoadingStateProps) {
  return (
    <section className="status-card panel-loading">
      <div className="spinner" aria-hidden="true" />
      <div>
        <p className="overline">Processing</p>
        <h2>Analyzing brief...</h2>
        <p className="helper-text">The backend is validating structured output before it returns.</p>
        {runId ? <p className="run-id">Run ID: {runId}</p> : null}
      </div>
    </section>
  );
}
