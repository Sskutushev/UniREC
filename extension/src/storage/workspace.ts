import type { BriefResult } from '../types/api';

const STORAGE_KEY = 'ai-brief-decoder-workspace';
const MAX_ITEMS = 12;

interface BrowserStorage {
  get: (keys?: string | string[] | object | null) => Promise<Record<string, unknown>>;
  set: (items: Record<string, unknown>) => Promise<void>;
}

export interface SavedRun {
  runId: string;
  input: string;
  summary: string;
  createdAt: string;
  result: BriefResult;
  unread: boolean;
}

export interface WorkspaceSnapshot {
  runs: SavedRun[];
  selectedRunId: string | null;
}

const initialSnapshot: WorkspaceSnapshot = {
  runs: [],
  selectedRunId: null,
};

function getChromeStorage(): BrowserStorage | null {
  const browserChrome = (globalThis as { chrome?: { storage?: { local?: BrowserStorage } } }).chrome;

  if (!browserChrome?.storage?.local) {
    return null;
  }

  return browserChrome.storage.local;
}

export async function loadWorkspaceSnapshot(): Promise<WorkspaceSnapshot> {
  const chromeStorage = getChromeStorage();

  if (chromeStorage) {
    const result = await chromeStorage.get(STORAGE_KEY);
    return (result[STORAGE_KEY] as WorkspaceSnapshot | undefined) ?? initialSnapshot;
  }

  const localValue = window.localStorage.getItem(STORAGE_KEY);
  return localValue ? (JSON.parse(localValue) as WorkspaceSnapshot) : initialSnapshot;
}

export async function saveWorkspaceSnapshot(snapshot: WorkspaceSnapshot): Promise<void> {
  const normalizedSnapshot: WorkspaceSnapshot = {
    runs: snapshot.runs.slice(0, MAX_ITEMS),
    selectedRunId: snapshot.selectedRunId,
  };

  const chromeStorage = getChromeStorage();

  if (chromeStorage) {
    await chromeStorage.set({ [STORAGE_KEY]: normalizedSnapshot });
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(normalizedSnapshot));
}
