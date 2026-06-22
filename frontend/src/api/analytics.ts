import client from './client';
import type { AnalyticsSummary } from '../types/analytics';

/**
 * 获取学习分析数据
 */
export async function getAnalytics(params: {
  sessionId?: string;
  subjectId?: string;
}): Promise<AnalyticsSummary> {
  const { data } = await client.get('/learning-analytics', { params });
  return data;
}
