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
      <div className="compose-info-bar">
        <span className="compose-info-bar-title">Brief Decoder</span>
        <div className="compose-badges">
          <span className="compose-badge">
            <span className="compose-badge-dot" />
            Fake provider
          </span>
          <span className="compose-badge">
            <span className="compose-badge-dot" />
            Pydantic validated
          </span>
          <span className="compose-badge">
            <span className="compose-badge-dot" />
            Structured JSON
          </span>
        </div>
      </div>

      <section className="compose-editor-card">
        <div className="compose-editor-header">
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
                ? `Add ${remaining} more characters to decode.`
                : 'Ready — goals, risks, questions, and next action.'}
            </p>
            {!isTooShort && !isLoading ? (
              <p className="sub-helper-text">Result opens in the Results tab.</p>
            ) : null}
          </div>

          <button className="primary-button" disabled={isDisabled} onClick={onSubmit} type="button">
            {isLoading ? 'Running…' : 'Run decode'}
          </button>
        </div>
      </section>
    </section>
  );
}
