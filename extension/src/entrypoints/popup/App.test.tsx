import { render, screen } from '@testing-library/react';

import { App } from './App';


describe('App', () => {
  it('renders the scaffold heading', async () => {
    render(<App />);

    expect(await screen.findByRole('heading', { name: 'AI Brief Decoder Lite' })).toBeInTheDocument();
  });
});
