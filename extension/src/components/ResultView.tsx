import { CopyButton } from './CopyButton';
import { RiskBadge } from './RiskBadge';
import type { BriefResult } from '../types/api';

interface ResultViewProps {
  result: BriefResult;
}

function renderList(title: string, items: string[]) {
  return (
    <section className="result-block">
      <div className="block-header">
        <p className="eyebrow">{title}</p>
      </div>
      <ul className="bullet-list">
        {items.map((item) => (
          <li key={`${title}-${item}`}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

export function ResultView({ result }: ResultViewProps) {
  return (
    <section className="panel panel-result">
      <div className="panel-header panel-header-tight">
        <div>
          <p className="eyebrow">Decoded output</p>
          <h2>Execution-ready brief</h2>
        </div>
        <div className="copy-actions">
          <CopyButton label="Copy summary" value={result.summary} />
          <CopyButton label="Copy JSON" value={JSON.stringify(result, null, 2)} />
        </div>
      </div>

      <section className="summary-card">
        <p className="eyebrow">Summary</p>
        <p>{result.summary}</p>
      </section>

      <div className="result-grid">
        {renderList('Goals', result.goals)}
        {renderList('Deliverables', result.deliverables)}
        {renderList('Constraints', result.constraints)}
      </div>

      <section className="result-block">
        <div className="block-header">
          <p className="eyebrow">Risks</p>
        </div>
        <div className="risk-list">
          {result.risks.map((risk) => (
            <article key={risk.risk} className="risk-card">
              <div className="risk-card-header">
                <strong>{risk.risk}</strong>
                <RiskBadge severity={risk.severity} />
              </div>
              <p>{risk.reason}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="result-block">
        <div className="block-header">
          <p className="eyebrow">Clarifying questions</p>
        </div>
        <ol className="number-list">
          {result.clarifying_questions.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ol>
      </section>

      <section className="cta-card">
        <p className="eyebrow">Recommended next action</p>
        <p>{result.recommended_next_action}</p>
      </section>
    </section>
  );
}
