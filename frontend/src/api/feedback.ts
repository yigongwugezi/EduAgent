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

// ── Learning Timeline ─────────────────────────────────────────────

export interface TimelineEvent {
  id: number;
  event: string;
  label: string;
  icon: string;
  color: string;
  resourceId: string;
  resourceTitle: string;
  resourceType: string;
  relatedStageId: string;
  relatedChapter: string;
  metadata: Record<string, unknown>;
  timestamp: number;
}

export interface TimelineResponse {
  events: TimelineEvent[];
  total: number;
}

export async function getLearningTimeline(
  sessionId: string,
  subjectId?: string,
  limit?: number,
): Promise<TimelineResponse> {
  const { data } = await client.get('/learning-events/timeline', {
    params: { sessionId, subjectId, limit },
  });
  return data;
}
