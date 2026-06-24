import { act, renderHook, waitFor } from '@testing-library/react';

import { ApiError } from '../api/client';
import type { DecodeRunResponse, DecodeRunStatus } from '../types/api';
import { useDecode } from './useDecode';

vi.mock('../api/client', () => ({
  ApiError: class extends Error {
    constructor(
      message: string,
      public readonly status: number,
      public readonly errorCode: string,
    ) {
      super(message);
    }
  },
  decodeBrief: vi.fn(),
  getRunStatus: vi.fn(),
}));

const { decodeBrief, getRunStatus } = await import('../api/client');

const completedResponse: DecodeRunResponse = {
  run_id: 'run-1',
  status: 'completed',
  result: {
    summary: 'Normalized summary',
    goals: ['Goal'],
    deliverables: ['Deliverable'],
    constraints: ['Constraint'],
    risks: [{ risk: 'Risk', severity: 'low', reason: 'Reason' }],
    clarifying_questions: ['Question?'],
    recommended_next_action: 'Do the next thing.',
  },
  error_code: null,
  error_message: null,
  created_at: '',
  updated_at: '',
  completed_at: '',
};


describe('useDecode', () => {
  it('handles a completed response immediately', async () => {
    vi.mocked(decodeBrief).mockResolvedValue(completedResponse);

    const { result } = renderHook(() => useDecode());
    await act(async () => {
      await result.current.run('Long enough brief body for decoding. '.repeat(3));
    });

    await waitFor(() => expect(result.current.state.phase).toBe('success'));
    expect(result.current.state.result?.summary).toBe('Normalized summary');
  });

  it('transitions to error state on API failure', async () => {
    vi.mocked(decodeBrief).mockRejectedValue(new ApiError('Decode failed', 502, 'provider_failure'));

    const { result } = renderHook(() => useDecode());
    await act(async () => {
      await result.current.run('Long enough brief body for decoding. '.repeat(3));
    });

    await waitFor(() => expect(result.current.state.phase).toBe('error'));
    expect(result.current.state.errorCode).toBe('provider_failure');
  });

  it('polls until a run completes', async () => {
    const pendingResponse: DecodeRunResponse = {
      ...completedResponse,
      status: 'running',
      result: null,
      completed_at: null,
    };
    const polledResponse: DecodeRunStatus = {
      ...completedResponse,
      input_text: 'brief',
      provider_name: 'fake',
    };

    vi.mocked(decodeBrief).mockResolvedValue(pendingResponse);
    vi.mocked(getRunStatus).mockResolvedValue(polledResponse);

    const { result } = renderHook(() => useDecode());
    await act(async () => {
      await result.current.run('Long enough brief body for decoding. '.repeat(3));
    });

    await waitFor(() => expect(result.current.state.phase).toBe('success'));
    expect(getRunStatus).toHaveBeenCalledWith('run-1');
  });
});
