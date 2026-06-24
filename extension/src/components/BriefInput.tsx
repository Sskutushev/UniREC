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
    <section className="panel panel-input">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Input</p>
          <h2>Paste a client brief</h2>
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

      <div className="panel-footer">
        <p className="helper-text">
          {isTooShort
            ? `Add ${remaining} more characters for a meaningful decode.`
            : 'The decoder returns a structured action-ready brief.'}
        </p>
        <button className="primary-button" disabled={isDisabled} onClick={onSubmit} type="button">
          {isLoading ? 'Running...' : 'Run decode'}
        </button>
      </div>
    </section>
  );
}
