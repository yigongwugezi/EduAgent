import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Clock, Eye, CheckCircle2, FileText, Code, MessageSquare,
  Target, BookOpen, ArrowRight, ExternalLink, History,
} from 'lucide-react';
import { useChatStore } from '../store/chatStore';
import { useSubjectStore } from '../store/subjectStore';
import { getLearningTimeline } from '../api/feedback';
import type { TimelineEvent } from '../api/feedback';
import { timeAgo } from '../utils/format';
import Loading from '../components/common/Loading';
import EmptyState from '../components/common/EmptyState';

/* ===================================================================
 * 事件图标映射
 * =================================================================== */
const EVENT_ICON: Record<string, React.ReactNode> = {
  resource_view:     <Eye className="w-4 h-4" />,
  resource_complete: <CheckCircle2 className="w-4 h-4" />,
  quiz_result:       <FileText className="w-4 h-4" />,
  practice_result:   <Code className="w-4 h-4" />,
  feedback:          <MessageSquare className="w-4 h-4" />,
  stage_complete:    <Target className="w-4 h-4" />,
  node_progress:     <BookOpen className="w-4 h-4" />,
};

const EVENT_COLOR_BG: Record<string, string> = {
  resource_view:     'bg-blue-100 text-blue-600',
  resource_complete: 'bg-green-100 text-green-600',
  quiz_result:       'bg-amber-100 text-amber-600',
  practice_result:   'bg-cyan-100 text-cyan-600',
  feedback:          'bg-purple-100 text-purple-600',
  stage_complete:    'bg-rose-100 text-rose-600',
  node_progress:     'bg-gray-100 text-gray-500',
};

const EVENT_LINE_COLOR: Record<string, string> = {
  resource_view:     'border-blue-300',
  resource_complete: 'border-green-300',
  quiz_result:       'border-amber-300',
  practice_result:   'border-cyan-300',
  feedback:          'border-purple-300',
  stage_complete:    'border-rose-300',
  node_progress:     'border-gray-200',
};

/* ===================================================================
 * 时间线条目
 * =================================================================== */
function TimelineItem({
  event,
  onNavigate,
}: {
  event: TimelineEvent;
  onNavigate: (resourceId: string, stageId: string) => void;
}) {
  // 从 metadata 提取 stage title
  const stageTitle = event.metadata?.stageTitle as string | undefined;
  const nodeStatus = event.metadata?.status as string | undefined;

  // 构建描述
  let description = '';
  if (event.resourceTitle) {
    description = event.resourceTitle;
  } else if (event.relatedChapter) {
    description = `章节：${event.relatedChapter}`;
  } else if (stageTitle) {
    description = stageTitle;
  } else if (event.relatedStageId) {
    description = `阶段 ${event.relatedStageId.replace(/[^0-9]/g, '')}`;
  } else if (nodeStatus) {
    description = `节点状态：${nodeStatus === 'completed' ? '已完成' : nodeStatus === 'in_progress' ? '学习中' : '已解锁'}`;
  }

  // quiz_result 显示正确率
  let detail = '';
  if (event.event === 'quiz_result' && event.metadata) {
    const correct = event.metadata.correct as number | undefined;
    const total = event.metadata.total as number | undefined;
    if (correct != null && total != null) {
      detail = `${correct}/${total} 正确`;
    }
    const accuracy = event.metadata.accuracy as number | undefined;
    if (accuracy != null && !detail) {
      detail = `正确率 ${accuracy}%`;
    }
  }
  if (event.event === 'feedback' && event.metadata) {
    const rating = event.metadata.rating as number | undefined;
    if (rating != null) {
      detail = `评分 ${'⭐'.repeat(rating)}`;
    }
  }

  const iconBg = EVENT_COLOR_BG[event.event] || 'bg-gray-100 text-gray-500';
  const lineColor = EVENT_LINE_COLOR[event.event] || 'border-gray-200';

  return (
    <div className="relative flex gap-4 pb-6 group">
      {/* 时间线竖线 */}
      <div className={`absolute left-[1.125rem] top-10 bottom-0 w-px border-l-2 border-dashed ${lineColor} last:hidden`} />

      {/* 图标 */}
      <div className={`relative z-10 w-9 h-9 rounded-xl ${iconBg} flex items-center justify-center flex-shrink-0 shadow-sm`}>
        {EVENT_ICON[event.event] || <History className="w-4 h-4" />}
      </div>

      {/* 内容 */}
      <div className="flex-1 min-w-0 pt-0.5">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-sm font-semibold text-gray-800">{event.label}</p>
            {description && (
              <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{description}</p>
            )}
            {detail && (
              <span className="inline-block mt-1 px-2 py-0.5 rounded-md text-[10px] font-medium bg-gray-50 text-gray-500 border border-gray-100">
                {detail}
              </span>
            )}
          </div>
          <span className="text-[10px] text-gray-400 whitespace-nowrap flex-shrink-0 mt-0.5">
            {timeAgo(event.timestamp)}
          </span>
        </div>

        {/* 跳转按钮 */}
        {(event.resourceId || event.relatedStageId) && (
          <div className="flex items-center gap-2 mt-2">
            {event.resourceId && (
              <button
                onClick={() => onNavigate(event.resourceId, '')}
                className="inline-flex items-center gap-1 text-[10px] font-medium text-brand-500 hover:text-brand-600 transition-colors"
              >
                <ExternalLink className="w-3 h-3" />
                查看资源
              </button>
            )}
            {event.relatedStageId && (
              <button
                onClick={() => onNavigate('', event.relatedStageId)}
                className="inline-flex items-center gap-1 text-[10px] font-medium text-gray-400 hover:text-gray-600 transition-colors"
              >
                <ArrowRight className="w-3 h-3" />
                跳转阶段
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ===================================================================
 * 主页面
 * =================================================================== */
export default function LearningTimelinePage() {
  const navigate = useNavigate();
  const sessionId = useChatStore((s) => s.currentSessionId);
  const subjectId = useSubjectStore((s) => s.activeSubject?.id);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    getLearningTimeline(sessionId, subjectId, 100)
      .then((res) => {
        setEvents(res.events || []);
        setTotal(res.total || 0);
      })
      .catch(() => {
        setError('加载学习时间线失败，请确认后端已启动');
        setEvents([]);
      })
      .finally(() => setLoading(false));
  }, [sessionId, subjectId]);

  // 按天分组
  const grouped = groupByDate(events);

  const handleNavigate = useCallback((resourceId: string, stageId: string) => {
    if (resourceId) {
      navigate(`/resources/${resourceId}`);
    } else if (stageId) {
      navigate(`/resources?relatedStageId=${encodeURIComponent(stageId)}`);
    }
  }, [navigate]);

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 md:py-8">
      {/* ========== 头部 ========== */}
      <div className="mb-6">
        <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-1 flex items-center gap-2">
          <History className="w-7 h-7 text-brand-500" />
          学习时间线
        </h1>
        <p className="text-sm text-gray-500">
          共 <span className="font-semibold text-gray-700">{total}</span> 条学习行为记录
        </p>
      </div>

      {/* ========== 列表 ========== */}
      {loading ? (
        <Loading text="加载时间线…" />
      ) : error ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="w-16 h-16 rounded-2xl bg-red-50 flex items-center justify-center mb-4">
            <History className="w-7 h-7 text-red-300" />
          </div>
          <h3 className="text-base font-semibold text-gray-700 mb-1">加载失败</h3>
          <p className="text-sm text-gray-400 mb-5">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-5 py-2.5 bg-gray-900 text-white rounded-xl text-sm font-semibold hover:bg-gray-800 transition-all"
          >
            刷新重试
          </button>
        </div>
      ) : events.length === 0 ? (
        <EmptyState
          icon={<History className="w-8 h-8" />}
          title="暂无学习行为记录"
          description="开始学习后，你的资源查看、练习提交、阶段完成等行为将显示在这里"
          action={
            <button
              onClick={() => navigate('/resources')}
              className="mt-3 px-5 py-2.5 bg-gray-900 text-white rounded-xl text-sm font-semibold hover:bg-gray-800 transition-all inline-flex items-center gap-2"
            >
              <BookOpen className="w-4 h-4" />
              前往资源库
            </button>
          }
        />
      ) : (
        <div className="space-y-1">
          {grouped.map(([dateLabel, dateEvents]) => (
            <div key={dateLabel}>
              {/* 日期分组标题 */}
              <div className="flex items-center gap-2 mb-3 mt-5 first:mt-0">
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-gray-100 text-gray-500 text-[10px] font-medium">
                  <Clock className="w-3 h-3" />
                  {dateLabel}
                </div>
                <div className="flex-1 h-px bg-gray-100" />
                <span className="text-[10px] text-gray-300">{dateEvents.length} 条</span>
              </div>

              {/* 当天的事件 */}
              <div className="pl-1">
                {dateEvents.map((evt) => (
                  <TimelineItem key={evt.id} event={evt} onNavigate={handleNavigate} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ===================================================================
 * 按日期分组工具
 * =================================================================== */
function groupByDate(events: TimelineEvent[]): [string, TimelineEvent[]][] {
  const groups = new Map<string, TimelineEvent[]>();

  const today = new Date();
  const todayStr = formatDateLabel(today);
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStr = formatDateLabel(yesterday);

  for (const evt of events) {
    const d = new Date(evt.timestamp);
    let label: string;
    const dateStr = formatDateLabel(d);

    if (dateStr === todayStr) {
      label = '今天';
    } else if (dateStr === yesterdayStr) {
      label = '昨天';
    } else {
      label = dateStr;
    }

    if (!groups.has(label)) groups.set(label, []);
    groups.get(label)!.push(evt);
  }

  return Array.from(groups.entries());
}

function formatDateLabel(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}
