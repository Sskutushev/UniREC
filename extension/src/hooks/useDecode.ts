import { useCallback, useMemo, useState } from 'react';

import { ApiError, decodeBrief, getRunStatus } from '../api/client';
import type { BriefResult, DecodeRunResponse, DecodeRunStatus } from '../types/api';

const POLL_INTERVAL_MS = 1500;
const POLL_TIMEOUT_MS = 60000;

type DecodePhase = 'idle' | 'loading' | 'success' | 'error';

export interface DecodeState {
  phase: DecodePhase;
  runId: string | null;
  result: BriefResult | null;
  errorCode: string | null;
  errorMessage: string | null;
}

const initialState: DecodeState = {
  phase: 'idle',
  runId: null,
  result: null,
  errorCode: null,
  errorMessage: null,
};

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function toErrorState(error: unknown): DecodeState {
  if (error instanceof ApiError) {
    return {
      phase: 'error',
      runId: null,
      result: null,
      errorCode: error.errorCode,
      errorMessage: error.message,
    };
  }

  return {
    phase: 'error',
    runId: null,
    result: null,
    errorCode: 'unexpected_error',
    errorMessage: 'Unexpected error while decoding the brief.',
  };
}

function isTerminal(response: DecodeRunResponse | DecodeRunStatus): boolean {
  return response.status === 'completed' || response.status === 'failed';
}

function toSuccessState(response: DecodeRunResponse | DecodeRunStatus): DecodeState {
  return {
    phase: 'success',
    runId: response.run_id,
    result: response.result,
    errorCode: response.error_code,
    errorMessage: response.error_message,
  };
}

export function useDecode() {
  const [state, setState] = useState<DecodeState>(initialState);

  const run = useCallback(async (text: string) => {
    setState({ ...initialState, phase: 'loading' });

    try {
      const response = await decodeBrief(text);
      setState((current) => ({ ...current, runId: response.run_id, phase: 'loading' }));

      if (isTerminal(response)) {
        setState(response.status === 'completed' ? toSuccessState(response) : toErrorState(new ApiError(response.error_message ?? 'Decode failed', 502, response.error_code ?? 'decode_failed')));
        return;
      }

      const startedAt = Date.now();
      let nextResponse: DecodeRunStatus = await getRunStatus(response.run_id);

      while (!isTerminal(nextResponse)) {
        if (Date.now() - startedAt > POLL_TIMEOUT_MS) {
          throw new ApiError('Polling timed out while waiting for the result.', 408, 'poll_timeout');
        }
        await delay(POLL_INTERVAL_MS);
        nextResponse = await getRunStatus(response.run_id);
      }

      if (nextResponse.status === 'failed') {
        throw new ApiError(
          nextResponse.error_message ?? 'Decode failed',
          502,
          nextResponse.error_code ?? 'decode_failed',
        );
      }

      setState(toSuccessState(nextResponse));
    } catch (error) {
      setState(toErrorState(error));
    }
  }, []);

  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  return useMemo(
    () => ({
      state,
      isLoading: state.phase === 'loading',
      run,
      reset,
    }),
    [reset, run, state],
  );
}
