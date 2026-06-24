import { fireEvent, render, screen } from '@testing-library/react';

import { BriefInput } from './BriefInput';


describe('BriefInput', () => {
  it('disables submit for short content and updates the textarea', () => {
    const handleChange = vi.fn();
    const handleSubmit = vi.fn();

    render(
      <BriefInput value="short brief" isLoading={false} onChange={handleChange} onSubmit={handleSubmit} />,
    );

    fireEvent.change(screen.getByPlaceholderText(/paste the raw brief/i), {
      target: { value: 'A longer brief body that should update the input state.' },
    });

    expect(handleChange).toHaveBeenCalled();
    expect(screen.getByRole('button', { name: /run decode/i })).toBeDisabled();
  });
});
