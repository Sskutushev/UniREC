import type { ReactNode } from 'react';

interface TopBarProps {
  historyCount: number;
  unreadCount: number;
  onHistoryClick: () => void;
  onNotificationsClick: () => void;
}

function HistoryIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24">
      <path d="M12 8v5l3 2" fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth="1.8" />
      <path
        d="M21 12a9 9 0 1 1-2.64-6.36M21 4v6h-6"
        fill="none"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function BellIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24">
      <path
        d="M15 18H5.5a1 1 0 0 1-.78-1.62L6 14.8V10a6 6 0 1 1 12 0v4.8l1.28 1.58A1 1 0 0 1 18.5 18H15Zm0 0a3 3 0 0 1-6 0"
        fill="none"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

interface ActionButtonProps {
  label: string;
  count: number;
  onClick: () => void;
  icon: ReactNode;
}

function ActionButton({ label, count, onClick, icon }: ActionButtonProps) {
  return (
    <button className="top-action" type="button" onClick={onClick} aria-label={label}>
      <span className="top-action-icon">{icon}</span>
      <span className="top-action-label">{label}</span>
      {count > 0 ? <span className="top-action-badge">{count}</span> : null}
    </button>
  );
}

export function TopBar({ historyCount, unreadCount, onHistoryClick, onNotificationsClick }: TopBarProps) {
  return (
    <header className="top-bar">
      <div className="top-bar-brand">
        <span className="top-bar-dot" aria-hidden="true" />
        <h1>AI Brief Decoder</h1>
      </div>
      <div className="top-actions">
        <ActionButton
          label="History"
          count={historyCount}
          onClick={onHistoryClick}
          icon={<HistoryIcon />}
        />
        <ActionButton
          label="Inbox"
          count={unreadCount}
          onClick={onNotificationsClick}
          icon={<BellIcon />}
        />
      </div>
    </header>
  );
}
