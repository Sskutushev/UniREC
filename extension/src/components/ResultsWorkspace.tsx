import { CopyButton } from './CopyButton';
import { ResultView } from './ResultView';
import type { SavedRun } from '../storage/workspace';

interface ResultsWorkspaceProps {
  activeRun: SavedRun | null;
  recentRuns: SavedRun[];
  onSelectRun: (runId: string) => void;
}

function formatTime(value: string): string {
  return new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function ResultsWorkspace({ activeRun, recentRuns, onSelectRun }: ResultsWorkspaceProps) {
  if (!activeRun) {
    return (
      <section className="workspace-panel workspace-empty-state">
        <p className="overline">Results</p>
        <h2>No decoded briefs yet</h2>
        <p className="muted-copy">
          Run the decoder from the Compose tab to see structured results here.
        </p>
      </section>
    );
  }

  return (
    <section className="workspace-panel results-shell">
      <div className="results-summary-strip">
        <div>
          <p className="overline">Current result</p>
          <h2>Decoded brief</h2>
        </div>
        <div className="copy-actions">
          <CopyButton label="Summary" value={activeRun.result.summary} />
          <CopyButton label="JSON" value={JSON.stringify(activeRun.result, null, 2)} />
        </div>
      </div>

      {recentRuns.length > 1 ? (
        <div className="recent-runs-strip">
          {recentRuns.map((run) => (
            <button
              key={run.runId}
              className={`recent-run-card ${run.runId === activeRun.runId ? 'recent-run-card-active' : ''}`}
              type="button"
              onClick={() => onSelectRun(run.runId)}
            >
              <span className="recent-run-time">{formatTime(run.createdAt)}</span>
              <strong>{run.summary}</strong>
              <span>{run.input.slice(0, 60)}…</span>
            </button>
          ))}
        </div>
      ) : null}

      <div className="workspace-scroll results-scroll">
        <ResultView result={activeRun.result} />
      </div>
    </section>
  );
}
