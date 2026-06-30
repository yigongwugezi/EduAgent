import client from './client';
import type { LearningPath } from '../types/learningPath';

/** 获取学习路径 */
export async function getLearningPath(params: { sessionId: string; subjectId?: string }): Promise<{ path: LearningPath }> {
  const { data } = await client.get('/api/learning-path', { params });
  return data;
}

/** 触发智能体生成学习路径 */
export async function generateLearningPath(params: {
  sessionId?: string;
  subjectId?: string;
  courseId?: string;
  userMessage?: string;
}): Promise<{ path: LearningPath }> {
  const { data } = await client.post('/api/learning-path/generate', params);
  return data;
}

/** 更新节点进度 */
export async function updateNodeProgress(
  nodeId: string,
  mastery: number,
  params: { sessionId: string; subjectId?: string; status?: string },
): Promise<void> {
  await client.patch(`/api/learning-path/nodes/${nodeId}`, { mastery, ...params });
}
