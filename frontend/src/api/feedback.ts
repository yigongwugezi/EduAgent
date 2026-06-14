import client from './client';

export interface SubmitFeedbackParams {
  sessionId?: string;
  resourceId: string;
  rating: number;          // 1-5
  comment?: string;
  difficultyMatch?: 'too_easy' | 'just_right' | 'too_hard';
}

export async function submitFeedback(params: SubmitFeedbackParams): Promise<void> {
  await client.post('/feedback', params);
}

export interface StudyEventParams {
  sessionId?: string;
  event: string;
  resourceId?: string;
  duration?: number;
  metadata?: Record<string, unknown>;
}

export async function logStudyEvent(params: StudyEventParams): Promise<void> {
  await client.post('/feedback/event', params);
}
