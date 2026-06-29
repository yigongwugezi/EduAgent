import client from './client';
import type { TodayTasksResponse, SessionTasksResponse, TaskCompleteResponse } from '../types/dailyTask';

/**
 * Get today's tasks across all subjects for the current learner.
 */
export async function getTodayTasks(params: {
  learnerId?: string;
  sessionId?: string;
}): Promise<TodayTasksResponse> {
  const { data } = await client.get('/daily-tasks/today', { params });
  return data;
}

/**
 * Get daily tasks for a specific session/learning path.
 */
export async function getSessionTasks(params: {
  sessionId: string;
  day?: number;
}): Promise<SessionTasksResponse> {
  const { data } = await client.get(`/learning-path/${params.sessionId}/daily-tasks`, {
    params: { day: params.day },
  });
  return data;
}

/**
 * Toggle completion status of a daily task.
 */
export async function completeTask(
  taskId: number,
  payload: { sessionId: string; completed: boolean },
): Promise<TaskCompleteResponse> {
  const { data } = await client.patch(`/daily-tasks/${taskId}/complete`, payload);
  return data;
}
