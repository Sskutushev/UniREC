import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { RiskBadge } from './RiskBadge';

describe('RiskBadge', () => {
  it.each([['low'], ['medium'], ['high']] as const)(
    'renders %s severity with correct class',
    (severity) => {
      render(<RiskBadge severity={severity} />);

      const badge = screen.getByText(severity);
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveClass(`risk-${severity}`);
    },
  );
});
