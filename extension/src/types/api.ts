export type Severity = 'low' | 'medium' | 'high';

export type RunStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface Risk {
  risk: string;
  severity: Severity;
  reason: string;
}

export interface BriefResult {
  summary: string;
  goals: string[];
  deliverables: string[];
  constraints: string[];
  risks: Risk[];
  clarifying_questions: string[];
  recommended_next_action: string;
}

export interface DecodeRunResponse {
  run_id: string;
  status: RunStatus;
  result: BriefResult | null;
  error_code: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface DecodeRunStatus extends DecodeRunResponse {
  input_text: string;
  provider_name: string | null;
}

export interface ApiErrorPayload {
  error_code: string;
  message: string;
}
