import { useEffect, useMemo, useRef, useState } from 'react';

import { BriefInput } from '../../components/BriefInput';
import { ErrorState } from '../../components/ErrorState';
import { InboxView } from '../../components/InboxView';
import { LoadingState } from '../../components/LoadingState';
import { ResultsWorkspace } from '../../components/ResultsWorkspace';
import { TabBar, type PopupTab } from '../../components/TabBar';
import { TopBar } from '../../components/TopBar';
import { useDecode } from '../../hooks/useDecode';
import {
  loadWorkspaceSnapshot,
  saveWorkspaceSnapshot,
  type SavedRun,
  type WorkspaceSnapshot,
} from '../../storage/workspace';

const EXAMPLE_BRIEF = `We need a landing page for a B2B SaaS analytics product.
The page should explain the product, include pricing teaser,
capture emails, and be ready in 2 weeks.
Budget is limited. We also need copy suggestions and basic SEO.`;

const emptyWorkspace: WorkspaceSnapshot = {
  runs: [],
  selectedRunId: null,
};

export function App() {
  const [brief, setBrief] = useState(EXAMPLE_BRIEF);
  const [activeTab, setActiveTab] = useState<PopupTab>('compose');
  const [workspace, setWorkspace] = useState<WorkspaceSnapshot>(emptyWorkspace);
  const { state, isLoading, run, reset } = useDecode();
  const processedRunIdRef = useRef<string | null>(null);

  useEffect(() => {
    void loadWorkspaceSnapshot().then(setWorkspace);
  }, []);

  useEffect(() => {
    if (state.phase !== 'success' || !state.result || !state.runId) {
      return;
    }

    if (processedRunIdRef.current === state.runId) {
      return;
    }

    processedRunIdRef.current = state.runId;

    const nextRun: SavedRun = {
      runId: state.runId,
      input: brief,
      summary: state.result.summary,
      createdAt: new Date().toISOString(),
      result: state.result,
      unread: true,
    };

    setWorkspace((current) => {
      const runs = [nextRun, ...current.runs.filter((item) => item.runId !== nextRun.runId)].slice(0, 12);
      const nextWorkspace = {
        runs,
        selectedRunId: nextRun.runId,
      };

      void saveWorkspaceSnapshot(nextWorkspace);
      return nextWorkspace;
    });

    setActiveTab('results');
  }, [brief, state.phase, state.result, state.runId]);

  const activeRun = useMemo(() => {
    if (workspace.selectedRunId) {
      return workspace.runs.find((item) => item.runId === workspace.selectedRunId) ?? workspace.runs[0] ?? null;
    }

    return workspace.runs[0] ?? null;
  }, [workspace.runs, workspace.selectedRunId]);

  const unreadCount = workspace.runs.filter((item) => item.unread).length;

  const selectRun = (runId: string, nextTab: PopupTab = 'results') => {
    setWorkspace((current) => {
      const runs = current.runs.map((item) =>
        item.runId === runId ? { ...item, unread: false } : item,
      );
      const nextWorkspace = {
        runs,
        selectedRunId: runId,
      };

      void saveWorkspaceSnapshot(nextWorkspace);
      return nextWorkspace;
    });

    setActiveTab(nextTab);
  };

  const surfaceState = useMemo(() => {
    if (state.phase === 'loading') {
      return <LoadingState runId={state.runId} />;
    }

    if (state.phase === 'error') {
      return (
        <ErrorState
          errorCode={state.errorCode}
          errorMessage={state.errorMessage}
          onRetry={() => {
            reset();
            setActiveTab('compose');
            void run(brief);
          }}
        />
      );
    }

    return null;
  }, [brief, reset, run, state.errorCode, state.errorMessage, state.phase, state.runId]);

  return (
    <main className="app-shell">
      <TopBar
        historyCount={workspace.runs.length}
        unreadCount={unreadCount}
        onHistoryClick={() => setActiveTab('results')}
        onNotificationsClick={() => setActiveTab('inbox')}
      />

      <TabBar activeTab={activeTab} onChange={setActiveTab} />

      {surfaceState ? <div className="surface-state-slot">{surfaceState}</div> : null}

      <div className="view-shell">
        {activeTab === 'compose' ? (
          <BriefInput
            value={brief}
            isLoading={isLoading}
            onChange={setBrief}
            onSubmit={() => void run(brief)}
          />
        ) : null}

        {activeTab === 'results' ? (
          <ResultsWorkspace activeRun={activeRun} recentRuns={workspace.runs} onSelectRun={selectRun} />
        ) : null}

        {activeTab === 'inbox' ? (
          <InboxView runs={workspace.runs} onOpenRun={(runId) => selectRun(runId, 'results')} />
        ) : null}
      </div>
    </main>
  );
}
