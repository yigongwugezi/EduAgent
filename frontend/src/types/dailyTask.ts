// ================================================================
// Daily Task types
// ================================================================

/** A single daily task item, possibly enriched with subject/session context. */
export interface DailyTask {
  id: number;
  sessionId: string;
  subjectId: string;
  subjectName: string;
  courseName?: string;
  stageId: string;
  dayIndex: number;
  dayLabel: string;
  title: string;
  description: string | null;
  completed: boolean;
  completedAt: number | null;
  source: string;
}

/** Response from GET /daily-tasks/today */
export interface TodayTasksResponse {
  tasks: DailyTask[];
  todayDate: string;
  completedCount: number;
  totalCount: number;
}

/** Per-session daily tasks response */
export interface SessionTasksResponse {
  tasks: DailyTask[];
  dayCount: number;
  currentDay: number;
  courseName?: string;
}

/** Response from PATCH /daily-tasks/{id}/complete */
export interface TaskCompleteResponse {
  ok: boolean;
  task: DailyTask;
}
