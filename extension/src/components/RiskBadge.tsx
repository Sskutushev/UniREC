import type { Severity } from '../types/api';

interface RiskBadgeProps {
  severity: Severity;
}

export function RiskBadge({ severity }: RiskBadgeProps) {
  return <span className={`risk-badge risk-${severity}`}>{severity}</span>;
}
