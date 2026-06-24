const ERROR_MESSAGES: Record<string, string> = {
  provider_failure: 'The provider failed. Retry with the fake provider or check the backend.',
  validation_error: 'Provider returned an invalid payload. Retry to generate a new result.',
  poll_timeout: 'The run timed out waiting for a result. Retry the request.',
  unexpected_error: 'Something unexpected happened while decoding the brief.',
};

interface ErrorStateProps {
  errorCode: string | null;
  errorMessage: string | null;
  onRetry: () => void;
}

export function ErrorState({ errorCode, errorMessage, onRetry }: ErrorStateProps) {
  const message =
    (errorCode && ERROR_MESSAGES[errorCode]) || errorMessage || ERROR_MESSAGES.unexpected_error;

  return (
    <section className="status-card panel-error">
      <div className="error-mark">!</div>
      <div>
        <p className="overline">Decode error</p>
        <h2>{errorCode ?? 'unexpected_error'}</h2>
        <p className="helper-text">{message}</p>
        <button className="primary-button" type="button" onClick={onRetry} style={{ marginTop: 8 }}>
          Retry
        </button>
      </div>
    </section>
  );
}
