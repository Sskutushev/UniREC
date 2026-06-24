interface BriefInputProps {
  value: string;
  isLoading: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

const MIN_CHARS = 50;
const MAX_CHARS = 10000;

export function BriefInput({ value, isLoading, onChange, onSubmit }: BriefInputProps) {
  const remaining = Math.max(MIN_CHARS - value.trim().length, 0);
  const isTooShort = value.trim().length < MIN_CHARS;
  const isTooLong = value.length > MAX_CHARS;
  const isDisabled = isLoading || isTooShort || isTooLong;

  return (
    <section className="workspace-panel compose-shell">
      <div className="compose-hero">
        <div>
          <p className="overline">Platform prototype</p>
          <h2>Operationalize raw briefs without leaving Chrome</h2>
          <p className="muted-copy compose-hero-copy">
            Normalize ambiguous requests, preserve run history, and route every finished decode into
            an enterprise-ready delivery workspace.
          </p>
        </div>
        <div className="compose-metrics">
          <div className="metric-card">
            <span>Provider</span>
            <strong>Fake / local</strong>
          </div>
          <div className="metric-card">
            <span>Output</span>
            <strong>Pydantic-safe</strong>
          </div>
          <div className="metric-card">
            <span>Routing</span>
            <strong>Results + inbox</strong>
          </div>
        </div>
      </div>

      <section className="compose-editor-card">
        <div className="panel-header">
          <div>
            <p className="overline">Input</p>
            <h3>Paste a client brief</h3>
          </div>
          <span className={`meter ${isTooShort ? 'meter-warning' : 'meter-ok'}`}>
            {value.length}/{MAX_CHARS}
          </span>
        </div>

        <textarea
          className="brief-textarea"
          value={value}
          disabled={isLoading}
          placeholder="Paste the raw brief, task, or project note here..."
          onChange={(event) => onChange(event.target.value)}
        />

        <div className="compose-footer">
          <div className="compose-guidance">
            <p className="helper-text">
              {isTooShort
                ? `Add ${remaining} more characters for a meaningful decode.`
                : 'Ready to generate a structured brief, risks, questions, and next action.'}
            </p>
            <p className="sub-helper-text">
              After completion, the result moves into the dedicated Results page and the Inbox feed.
            </p>
          </div>

          <button className="primary-button primary-button-wide" disabled={isDisabled} onClick={onSubmit} type="button">
            {isLoading ? 'Running decode' : 'Run decode'}
          </button>
        </div>
      </section>
    </section>
  );
}
