import client from './client';
import type { LearningPath } from '../types/learningPath';

export async function getLearningPath(params: { sessionId: string; subjectId?: string }): Promise<{ path: LearningPath }> {
  const { data } = await client.get('/api/learning-path', { params });
  return data;
}

export async function generateLearningPath(params: {
  sessionId?: string;
  subjectId?: string;
  targetTopics?: string[];
}): Promise<{ path: LearningPath }> {
  const { data } = await client.post('/api/learning-path/generate', params);
  return data;
}

export async function updateNodeProgress(
  nodeId: string,
  mastery: number,
  params: { sessionId: string; subjectId?: string; status?: string },
): Promise<void> {
  await client.patch(`/api/learning-path/nodes/${nodeId}`, { mastery, ...params });
}
