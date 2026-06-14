import client from './client';
import type { LearningPath } from '../types/learningPath';

export async function getLearningPath(sessionId?: string): Promise<{ path: LearningPath }> {
  const { data } = await client.get('/learning-path', { params: { sessionId } });
  return data;
}

export async function generateLearningPath(params: {
  sessionId?: string;
  targetTopics?: string[];
}): Promise<{ path: LearningPath }> {
  const { data } = await client.post('/learning-path/generate', params);
  return data;
}

export async function updateNodeProgress(nodeId: string, mastery: number, sessionId?: string): Promise<void> {
  await client.patch(`/learning-path/nodes/${nodeId}`, { mastery, sessionId });
}
