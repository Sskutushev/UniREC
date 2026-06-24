import { useMemo, useState } from 'react';

import { BriefInput } from '../../components/BriefInput';
import { ErrorState } from '../../components/ErrorState';
import { LoadingState } from '../../components/LoadingState';
import { ResultView } from '../../components/ResultView';
import { useDecode } from '../../hooks/useDecode';

const EXAMPLE_BRIEF = `We need a landing page for a B2B SaaS analytics product.
The page should explain the product, include pricing teaser,
capture emails, and be ready in 2 weeks.
Budget is limited. We also need copy suggestions and basic SEO.`;

export function App() {
  const [brief, setBrief] = useState(EXAMPLE_BRIEF);
  const { state, isLoading, run, reset } = useDecode();

  const decodedResult = state.phase === 'success' ? state.result : null;

  const headerMeta = useMemo(
    () => ({
      caption: 'Platform prototype',
      title: 'AI Brief Decoder Lite',
      subtitle: 'Turn ambiguous client requests into a structured delivery plan inside the extension.',
    }),
    [],
  );

  return (
    <main className="app-shell">
      <header className="hero-panel">
        <p className="eyebrow">{headerMeta.caption}</p>
        <h1>{headerMeta.title}</h1>
        <p className="hero-copy">{headerMeta.subtitle}</p>
      </header>

      <BriefInput
        value={brief}
        isLoading={isLoading}
        onChange={setBrief}
        onSubmit={() => void run(brief)}
      />

      {state.phase === 'loading' ? <LoadingState runId={state.runId} /> : null}

      {state.phase === 'error' ? (
        <ErrorState
          errorCode={state.errorCode}
          errorMessage={state.errorMessage}
          onRetry={() => {
            reset();
            void run(brief);
          }}
        />
      ) : null}

      {decodedResult ? <ResultView result={decodedResult} /> : null}
    </main>
  );
}
