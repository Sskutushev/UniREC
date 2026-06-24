import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { InboxView } from './InboxView';
import type { SavedRun } from '../storage/workspace';
import type { BriefResult } from '../types/api';

const fakeResult: BriefResult = {
  summary: 'B2B landing page brief decoded.',
  goals: ['Explain product clearly'],
  deliverables: ['Landing page'],
  constraints: ['Two-week deadline'],
  risks: [{ risk: 'Tight timeline', severity: 'high', reason: 'Scope is broad.' }],
  clarifying_questions: ['What is the primary CTA?'],
  recommended_next_action: 'Confirm CTA and audience.',
};

function makeRun(overrides?: Partial<SavedRun>): SavedRun {
  return {
    runId: 'run-1',
    input: 'We need a landing page...',
    summary: 'B2B landing page brief decoded.',
    createdAt: new Date('2025-01-01T10:00:00Z').toISOString(),
    result: fakeResult,
    unread: false,
    ...overrides,
  };
}

describe('InboxView', () => {
  it('shows empty state when there are no runs', () => {
    render(<InboxView runs={[]} onOpenRun={vi.fn()} />);

    expect(screen.getByText('No notifications yet')).toBeInTheDocument();
  });

  it('renders a notification card for each run', () => {
    const runs = [makeRun({ runId: 'run-1' }), makeRun({ runId: 'run-2', summary: 'Second run' })];
    render(<InboxView runs={runs} onOpenRun={vi.fn()} />);

    expect(screen.getByText('B2B landing page brief decoded.')).toBeInTheDocument();
    expect(screen.getByText('Second run')).toBeInTheDocument();
  });

  it('shows unread dot for unread runs', () => {
    render(<InboxView runs={[makeRun({ unread: true })]} onOpenRun={vi.fn()} />);

    expect(screen.getByLabelText('Unread result')).toBeInTheDocument();
  });

  it('calls onOpenRun with the correct runId when a card is clicked', () => {
    const onOpenRun = vi.fn();
    render(<InboxView runs={[makeRun({ runId: 'run-xyz' })]} onOpenRun={onOpenRun} />);

    fireEvent.click(screen.getByRole('button', { name: /open full brief/i }));

    expect(onOpenRun).toHaveBeenCalledWith('run-xyz');
  });
});
