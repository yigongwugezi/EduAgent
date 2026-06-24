// ================================================================
// Learning Analytics types
// ================================================================

/** 薄弱知识点数据结构 — 来自后端 /learning-analytics + diagnosis_agent */
export interface WeakTopic {
  topic: string;
  wrongCount: number;
  totalCount: number;
  risk: number;
  /** 来源: quiz, practice, feedback, diagnosis */
  source: string[];
  /** 优先级: high | medium | low */
  priority?: string;
  /** 掌握度 (0-100) */
  mastery?: number;
  /** 推荐原因 */
  reason?: string;
}

/** 热门资源 */
export interface TopResource {
  resourceId: string;
  count: number;
  title?: string;
}

/** 完成趋势数据点 */
export interface CompletionTrendPoint {
  date: string;
  count: number;
}

/** Quiz 趋势数据点 */
export interface QuizTrendPoint {
  date: string;
  accuracy: number;
  topic: string;
  timestamp: string;
}

/** 最近事件 */
export interface RecentEvent {
  event: string;
  resourceId?: string;
  timestamp?: number | string;
  metadata?: Record<string, unknown>;
}

/** 学习分析汇总 — 后端 /learning-analytics 返回 */
export interface AnalyticsSummary {
  eventCount: number;
  totalStudyMinutes: number;
  activeResourceCount: number;
  /** 查看资源次数（后端直接返回，前端也可从 eventBreakdown 推导） */
  resourceViewCount?: number;
  /** 完成资源次数 */
  resourceCompleteCount?: number;
  /** 查看资源次数（同 resourceViewCount，语义化命名） */
  viewedResources: number;
  /** 完成资源次数（同 resourceCompleteCount，语义化命名） */
  completedResources: number;
  /** 实践次数 */
  practiceCount: number;
  /** 最近学习时间（epoch ms，后端直接返回） */
  lastStudyTime?: number | null;
  eventBreakdown: Record<string, number>;
  topResources: TopResource[];
  quizAccuracy: number | null;
  weakTopics: WeakTopic[];
  recommendations: string[];
  completionTrend: CompletionTrendPoint[];
  quizTrend: QuizTrendPoint[];
  resourceTypeBreakdown: Record<string, number>;
  recentEvents: RecentEvent[];
  summary: string;
}

/** 时间线事件 — 后端 /learning-events/timeline 返回 */
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
