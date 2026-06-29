import { useCallback, useEffect, useState } from 'react';
import * as dailyTasksApi from '../api/dailyTasks';
import type { DailyTask } from '../types/dailyTask';
import { getCurrentLearner } from '../pages/LoginPage';
import { useChatStore } from '../store/chatStore';

/**
 * Hook for fetching and managing daily tasks.
 *
 * Automatically fetches today's tasks across all subjects on mount
 * and when dataVersion bumps (agent pipeline completion).
 */
export function useDailyTasks() {
  const [tasks, setTasks] = useState<DailyTask[]>([]);
  const [completedCount, setCompletedCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const learner = getCurrentLearner();
  const learnerId = learner?.id;
  const dataVersion = useChatStore((s) => s.dataVersion);

  const fetchTodayTasks = useCallback(async () => {
    if (!learnerId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await dailyTasksApi.getTodayTasks({ learnerId });
      setTasks(data.tasks || []);
      setCompletedCount(data.completedCount || 0);
      setTotalCount(data.totalCount || 0);
    } catch (e) {
      setError(e instanceof Error ? e.message : '加载今日任务失败');
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }, [learnerId]);

  const toggleTask = useCallback(async (task: DailyTask) => {
    // Optimistic update
    setTasks((prev) =>
      prev.map((t) =>
        t.id === task.id ? { ...t, completed: !t.completed } : t
      )
    );
    setCompletedCount((prev) =>
      task.completed ? prev - 1 : prev + 1
    );

    try {
      await dailyTasksApi.completeTask(task.id, {
        sessionId: task.sessionId,
        completed: !task.completed,
      });
    } catch (_e) {
      // Revert on failure
      setTasks((prev) =>
        prev.map((t) =>
          t.id === task.id ? { ...t, completed: task.completed } : t
        )
      );
      setCompletedCount((prev) =>
        task.completed ? prev + 1 : prev - 1
      );
    }
  }, []);

  // Fetch on mount and when page becomes visible
  useEffect(() => {
    fetchTodayTasks();
    const onVisible = () => {
      if (document.visibilityState === 'visible') {
        fetchTodayTasks();
      }
    };
    document.addEventListener('visibilitychange', onVisible);
    return () => document.removeEventListener('visibilitychange', onVisible);
  }, [fetchTodayTasks]);

  // Refresh after agent pipeline completes (dataVersion bump)
  useEffect(() => {
    if (dataVersion > 0) {
      fetchTodayTasks();
    }
  }, [dataVersion, fetchTodayTasks]);

  // Group tasks by subject for UI rendering
  const tasksBySubject = tasks.reduce<Record<string, DailyTask[]>>(
    (acc, task) => {
      const key = task.subjectId || 'default';
      if (!acc[key]) acc[key] = [];
      acc[key].push(task);
      return acc;
    },
    {}
  );

  return {
    tasks,
    tasksBySubject,
    completedCount,
    totalCount,
    loading,
    error,
    refetch: fetchTodayTasks,
    toggleTask,
  };
}
