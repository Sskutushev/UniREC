export type PopupTab = 'compose' | 'results' | 'inbox';

interface TabBarProps {
  activeTab: PopupTab;
  onChange: (tab: PopupTab) => void;
}

const tabs: Array<{ value: PopupTab; label: string }> = [
  { value: 'compose', label: 'Compose' },
  { value: 'results', label: 'Results' },
  { value: 'inbox', label: 'Inbox' },
];

export function TabBar({ activeTab, onChange }: TabBarProps) {
  return (
    <nav className="tab-bar" aria-label="Workspace sections">
      {tabs.map((tab) => (
        <button
          key={tab.value}
          className={`tab-button ${activeTab === tab.value ? 'tab-button-active' : ''}`}
          type="button"
          onClick={() => onChange(tab.value)}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
