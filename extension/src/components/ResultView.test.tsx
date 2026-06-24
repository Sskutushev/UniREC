import { render, screen } from '@testing-library/react';

import { ResultView } from './ResultView';


const result = {
  summary: 'A normalized summary of the client request.',
  goals: ['Explain the product'],
  deliverables: ['Landing page copy'],
  constraints: ['Budget is limited'],
  risks: [
    {
      risk: 'Scope creep',
      severity: 'medium' as const,
      reason: 'The brief asks for SEO and copy in the same sprint.',
    },
  ],
  clarifying_questions: ['Who signs off the copy?'],
  recommended_next_action: 'Confirm audience and CTA.',
};


describe('ResultView', () => {
  it('renders the structured result', () => {
    render(<ResultView result={result} />);

    expect(screen.getByText(result.summary)).toBeInTheDocument();
    expect(screen.getByText('Scope creep')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /copy json/i })).toBeInTheDocument();
  });
});
