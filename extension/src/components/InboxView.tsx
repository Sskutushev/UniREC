import type { SavedRun } from '../storage/workspace';

interface InboxViewProps {
  runs: SavedRun[];
  onOpenRun: (runId: string) => void;
}

function formatTimestamp(value: string): string {
  return new Date(value).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function InboxView({ runs, onOpenRun }: InboxViewProps) {
  return (
    <section className="workspace-panel inbox-shell">
      <div className="section-header">
        <div>
          <p className="overline">Notifications</p>
          <h2>Result delivery feed</h2>
        </div>
        <p className="muted-copy">Newly completed decodes surface here as mini updates.</p>
      </div>

      <div className="workspace-scroll inbox-scroll">
        {runs.length === 0 ? (
          <section className="workspace-empty-card">
            <h3>No notifications yet</h3>
            <p className="muted-copy">
              Once a decode finishes, a concise activity card appears here and links back to the
              full result screen.
            </p>
          </section>
        ) : (
          runs.map((run) => (
            <button key={run.runId} className="notification-card" type="button" onClick={() => onOpenRun(run.runId)}>
              <div className="notification-card-topline">
                <span className="notification-card-time">{formatTimestamp(run.createdAt)}</span>
                {run.unread ? <span className="notification-dot" aria-label="Unread result" /> : null}
              </div>
              <strong>{run.summary}</strong>
              <p>{run.result.recommended_next_action}</p>
              <span className="notification-link">Open full brief</span>
            </button>
          ))
        )}
      </div>
    </section>
  );
}
