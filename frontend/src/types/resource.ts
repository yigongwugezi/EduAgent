// ================================================================
// Resource types
// ================================================================

import type { ResourceType } from './chat';

export type ResourceFormat = 'text' | 'diagram' | 'video' | 'code' | 'quiz';

export interface Resource {
  id: string;
  type: ResourceType;
  title: string;
  description: string;
  content: string;          // Markdown body
  knowledgePoints: string[];
  tags: string[];
  difficulty: 'easy' | 'medium' | 'hard';
  estimatedMinutes: number;
  format: ResourceFormat;
  /** Mermaid 图谱定义 (mindmap 类型) */
  mermaidDef?: string;
  /** 代码内容 (case_study 类型) */
  codeBlocks?: CodeBlock[];
  /** 题目 (quiz 类型) */
  questions?: QuizQuestion[];
  /** PPT 大纲 */
  pptOutline?: PptSlide[];
  createdAt: number;
  /** 数据来源 */
  source?: 'user_input' | 'agent_generated' | 'system_inferred';
  /** 是否已收藏 */
  bookmarked?: boolean;
  /** 学习状态 */
  studyStatus?: 'new' | 'in_progress' | 'completed';

  // ========== ResourceAgent P0 新增字段 ==========
  /** 关联的学习阶段 ID */
  relatedStageId?: string;
  /** 关联的子阶段/任务 ID (如 stage_1_node_2) */
  taskId?: string;
  /** 关联的章节名称 */
  relatedChapter?: string;
  /** 关联的知识点列表 */
  relatedKnowledgePoints?: string[];
  /** 质检状态: passed / needs_review / fallback_passed */
  qualityStatus?: string;
}

export interface CodeBlock {
  language: string;
  code: string;
  explanation?: string;
}

export interface QuizQuestion {
  id: string;
  type: 'choice' | 'truefalse' | 'short_answer' | 'code';
  stem: string;
  options?: string[];
  answer: string;
  explanation: string;
  knowledgePoint: string;
  difficulty: 'easy' | 'medium' | 'hard';
}

export interface PptSlide {
  title: string;
  bullets: string[];
  notes?: string;
}

export type SortBy =
  | 'default'    // 默认推荐：已完成靠后 → 有阶段优先 → 最新
  | 'newest'     // 最新生成
  | 'shortest'   // 预计时间短优先
  | 'easiest'    // 难度从低到高
  | 'hardest'    // 难度从高到低
  | 'status'     // 已完成 / 未完成
  | 'stage';     // 当前阶段优先

export interface ResourceFilter {
  type?: ResourceType;
  difficulty?: string;
  source?: string;
  knowledgePoint?: string;
  format?: ResourceFormat;
  search?: string;
  sortBy?: SortBy;
  relatedStageId?: string;
  taskId?: string;
  resourceIds?: string;
  /** 章节筛选 */
  chapter?: string;
  /** 质检状态: passed | needs_review | fallback_passed */
  qualityStatus?: string;
  /** 学习状态: new | in_progress | completed */
  studyStatus?: string;
  /** 收藏筛选: "true" | "false" */
  bookmarked?: string;
}
