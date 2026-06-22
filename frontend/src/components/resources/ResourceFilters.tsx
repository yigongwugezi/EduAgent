import { Filter, SlidersHorizontal, RotateCcw, Layers, BookmarkCheck, BookmarkX, Square, CheckSquare } from 'lucide-react';
import type { ResourceType, DataSource } from '../../types/resource';
import { RESOURCE_TYPE_LABELS } from '../../utils/constants';

const difficultyLabel: Record<string, string> = { easy: '基础', medium: '进阶', hard: '挑战' };

const FILTER_TYPES: (ResourceType | undefined)[] = [
  undefined, 'lecture', 'mindmap', 'quiz', 'reading', 'case_study', 'video', 'ppt',
];

const QUALITY_STATUS_OPTIONS = [
  { value: undefined, label: '不限' }, { value: 'passed', label: '已通过' },
  { value: 'needs_review', label: '需复核' }, { value: 'fallback_passed', label: '兜底通过' },
] as const;

const STUDY_STATUS_OPTIONS = [
  { value: undefined, label: '不限' }, { value: 'new', label: '未开始' },
  { value: 'in_progress', label: '学习中' }, { value: 'completed', label: '已完成' },
] as const;

const BOOKMARKED_OPTIONS = [
  { value: undefined, label: '不限' }, { value: 'true', label: '已收藏' }, { value: 'false', label: '未收藏' },
] as const;

interface Props {
  active: ResourceType | undefined;
  onFilter: (type: ResourceType | undefined) => void;
  onSelectDifficulty: (level: string | undefined) => void;
  activeDifficulty: string | undefined;
  dataSource?: DataSource | undefined;
  onSelectSource: (s: DataSource | undefined) => void;
  activeQuality?: string | undefined;
  onSelectQuality: (q: string | undefined) => void;
  activeStudyStatus?: string | undefined;
  onSelectStudyStatus: (s: string | undefined) => void;
  activeBookmarked?: string | undefined;
  onSelectBookmarked: (b: string | undefined) => void;
  availableChapters: string[];
  activeChapter?: string | undefined;
  onSelectChapter: (c: string | undefined) => void;
  showFilters: boolean;
  onToggleFilters: () => void;
  hasActiveFilters: boolean;
  onClearAll: () => void;
}

export default function ResourceFilters({
  active, onFilter, onSelectDifficulty, activeDifficulty, dataSource, onSelectSource,
  activeQuality, onSelectQuality, activeStudyStatus, onSelectStudyStatus,
  activeBookmarked, onSelectBookmarked, availableChapters, activeChapter, onSelectChapter,
  showFilters, onToggleFilters, hasActiveFilters, onClearAll,
}: Props) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        <Filter className="w-4 h-4 text-gray-400 flex-shrink-0" />
        {FILTER_TYPES.map((t) => (
          <button key={t || 'all'} onClick={() => onFilter(t)}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${active === t ? 'bg-gray-900 text-white shadow-sm' : 'bg-white border border-gray-200 text-gray-500 hover:border-gray-300 hover:bg-gray-50'}`}>
            {t ? RESOURCE_TYPE_LABELS[t] : '全部'}
          </button>
        ))}
        <button onClick={onToggleFilters}
          className={`ml-auto px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all flex items-center gap-1.5 ${showFilters || hasActiveFilters ? 'bg-brand-50 text-brand-600 border border-brand-200' : 'bg-white border border-gray-200 text-gray-400 hover:border-gray-300'}`}>
          <SlidersHorizontal className="w-3.5 h-3.5" />
          {showFilters ? '收起筛选' : '更多筛选'}
          {hasActiveFilters && <span className="w-2 h-2 rounded-full bg-brand-500" />}
        </button>
      </div>

      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-gray-400 flex-shrink-0">难度：</span>
          {[undefined, 'easy', 'medium', 'hard'].map((level) => (
            <button key={level || 'all-diff'} onClick={() => onSelectDifficulty(level)}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-medium transition-all ${activeDifficulty === level ? 'bg-gray-800 text-white' : 'bg-gray-50 text-gray-500 hover:bg-gray-100'}`}>
              {level ? difficultyLabel[level] : '不限'}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-gray-400 flex-shrink-0">来源：</span>
          {([undefined, 'agent_generated', 'system_inferred', 'fallback', 'user_input'] as (DataSource | undefined)[]).map((s) => (
            <button key={s || 'all-src'} onClick={() => onSelectSource(s)}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-medium transition-all ${dataSource === s ? 'bg-gray-800 text-white' : 'bg-gray-50 text-gray-500 hover:bg-gray-100'}`}>
              {s ? (s === 'agent_generated' ? '智能体生成' : s === 'system_inferred' ? '系统推断' : s === 'fallback' ? '兜底' : '用户输入') : '不限'}
            </button>
          ))}
        </div>
        {hasActiveFilters && (
          <button onClick={onClearAll}
            className="px-2.5 py-1 rounded-lg text-[10px] font-medium text-red-500 bg-red-50 border border-red-100 hover:bg-red-100 transition-all flex items-center gap-1">
            <RotateCcw className="w-3 h-3" />清空筛选
          </button>
        )}
      </div>

      {showFilters && (
        <div className="p-4 bg-gray-50/80 border border-gray-100 rounded-xl space-y-3 animate-fade-in-up">
          {availableChapters.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px] text-gray-400 flex-shrink-0 flex items-center gap-1"><Layers className="w-3 h-3" /> 章节：</span>
              <button onClick={() => onSelectChapter(undefined)}
                className={`px-2.5 py-1 rounded-lg text-[10px] font-medium transition-all ${!activeChapter ? 'bg-gray-800 text-white' : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-50'}`}>不限</button>
              {availableChapters.map((ch) => (
                <button key={ch} onClick={() => onSelectChapter(ch)}
                  className={`px-2.5 py-1 rounded-lg text-[10px] font-medium transition-all ${activeChapter === ch ? 'bg-gray-800 text-white' : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-50'}`}>{ch}</button>
              ))}
            </div>
          )}
          <div className="flex items-center gap-6 flex-wrap">
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] text-gray-400 flex-shrink-0">质检：</span>
              {QUALITY_STATUS_OPTIONS.map((opt) => (
                <button key={opt.value || 'all-qs'} onClick={() => onSelectQuality(opt.value)}
                  className={`px-2.5 py-1 rounded-lg text-[10px] font-medium transition-all ${activeQuality === opt.value ? 'bg-gray-800 text-white' : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-50'}`}>{opt.label}</button>
              ))}
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] text-gray-400 flex-shrink-0">状态：</span>
              {STUDY_STATUS_OPTIONS.map((opt) => (
                <button key={opt.value || 'all-ss'} onClick={() => onSelectStudyStatus(opt.value)}
                  className={`px-2.5 py-1 rounded-lg text-[10px] font-medium transition-all ${activeStudyStatus === opt.value ? 'bg-gray-800 text-white' : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-50'}`}>{opt.label}</button>
              ))}
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] text-gray-400 flex-shrink-0">收藏：</span>
              {BOOKMARKED_OPTIONS.map((opt) => (
                <button key={opt.value || 'all-bm'} onClick={() => onSelectBookmarked(opt.value)}
                  className={`px-2.5 py-1 rounded-lg text-[10px] font-medium transition-all ${activeBookmarked === opt.value ? 'bg-gray-800 text-white' : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-50'}`}>
                  {opt.value === 'true' ? <BookmarkCheck className="w-3 h-3 inline mr-0.5" /> : opt.value === 'false' ? <BookmarkX className="w-3 h-3 inline mr-0.5" /> : null}
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
