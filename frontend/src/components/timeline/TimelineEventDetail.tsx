import { BookOpen, Target } from 'lucide-react';
import type { TimelineEvent } from '../../types/analytics';
import { timeAgo } from '../../utils/format';

/* ===================================================================
 * 事件类型标签映射
 * =================================================================== */
const RESOURCE_TYPE_LABELS: Record<string, string> = {
  lecture: '课程讲义',
  mindmap: '思维导图',
  quiz: '练习题',
  reading: '拓展阅读',
  case_study: '实操案例',
  video: '教学视频',
  ppt: 'PPT 大纲',
};

/* ===================================================================
 * Props
 * =================================================================== */
interface TimelineEventDetailProps {
  event: TimelineEvent;
}

/* ===================================================================
 * TimelineEventDetail — 单条事件展开详情
 * 根据事件类型展示不同的元数据信息
 * =================================================================== */
export default function TimelineEventDetail({ event }: TimelineEventDetailProps) {
  const meta = event.metadata || {};

  return (
    <div className="mt-3 pt-3 border-t border-gray-100 space-y-3 animate-fade-in-up">
      {/* ── Quiz 事件详情 ── */}
      {event.event === 'quiz_result' && (
        <QuizDetail meta={meta} timestamp={event.timestamp} />
      )}

      {/* ── Practice 事件详情 ── */}
      {event.event === 'practice_result' && (
        <PracticeDetail meta={meta} />
      )}

      {/* ── Feedback 事件详情 ── */}
      {event.event === 'feedback' && (
        <FeedbackDetail meta={meta} />
      )}

      {/* ── Resource 事件详情（view + complete） ── */}
      {(event.event === 'resource_view' || event.event === 'resource_complete') && (
        <ResourceDetail event={event} meta={meta} />
      )}

      {/* ── Node / Stage 进度事件详情 ── */}
      {(event.event === 'node_progress' || event.event === 'stage_complete') && (
        <NodeProgressDetail meta={meta} event={event} />
      )}

      {/* ── 兜底：展示原始 metadata ── */}
      {!['quiz_result', 'practice_result', 'feedback', 'resource_view', 'resource_complete', 'node_progress', 'stage_complete'].includes(event.event) && (
        <div className="p-3 bg-gray-50 rounded-xl">
          <pre className="text-[10px] text-gray-400 font-mono whitespace-pre-wrap">
            {JSON.stringify(meta, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

/* ===================================================================
 * Sub: Quiz 详情
 * =================================================================== */
function QuizDetail({ meta, timestamp }: { meta: Record<string, unknown>; timestamp: number }) {
  const correct = meta.correct as number | undefined;
  const total = meta.total as number | undefined;
  const accuracy = meta.accuracy as number | undefined;
  const score = meta.score as number | undefined;
  const duration = meta.duration as number | undefined;
  const topic = meta.topic as string | undefined;

  const accuracyValue = accuracy ?? (correct != null && total != null ? Math.round((correct / total) * 100) : undefined);

  return (
    <div className="p-3 bg-amber-50/60 border border-amber-100 rounded-xl space-y-2">
      <h4 className="text-xs font-semibold text-amber-700 flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
        练习详情
      </h4>
      <div className="grid grid-cols-2 gap-2 text-[11px]">
        {correct != null && total != null && (
          <>
            <InfoItem label="得分" value={`${correct}/${total}`} />
            <InfoItem label="正确率" value={accuracyValue != null ? `${accuracyValue}%` : '-'} />
          </>
        )}
        {score != null && <InfoItem label="评分" value={`${score}`} />}
        {topic && <InfoItem label="知识点" value={topic} />}
        {duration != null && <InfoItem label="用时" value={`${duration} 分钟`} />}
        <InfoItem label="提交时间" value={timeAgo(timestamp)} />
      </div>
    </div>
  );
}

/* ===================================================================
 * Sub: Practice 详情
 * =================================================================== */
function PracticeDetail({ meta }: { meta: Record<string, unknown> }) {
  const status = meta.status as string | undefined;
  const completionNotes = meta.completionNotes as string | undefined;
  const evaluation = meta.evaluation as string | undefined;
  const rating = meta.rating as number | undefined;
  const codeLang = meta.codeLang as string | undefined;

  const statusLabel =
    status === 'completed' ? '已完成' :
    status === 'in_progress' ? '进行中' :
    status === 'failed' ? '未通过' :
    status || '-';

  return (
    <div className="p-3 bg-cyan-50/60 border border-cyan-100 rounded-xl space-y-2">
      <h4 className="text-xs font-semibold text-cyan-700 flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
        实践详情
      </h4>
      <div className="grid grid-cols-2 gap-2 text-[11px]">
        <InfoItem label="状态" value={statusLabel} />
        {codeLang && <InfoItem label="编程语言" value={codeLang} />}
        {rating != null && <InfoItem label="评分" value={'⭐'.repeat(rating)} />}
      </div>
      {completionNotes && (
        <div className="text-[11px] text-gray-600 mt-1">
          <span className="text-gray-400">完成说明：</span>
          {completionNotes}
        </div>
      )}
      {evaluation && (
        <div className="text-[11px] text-gray-600">
          <span className="text-gray-400">评价：</span>
          {evaluation}
        </div>
      )}
    </div>
  );
}

/* ===================================================================
 * Sub: Feedback 详情
 * =================================================================== */
function FeedbackDetail({ meta }: { meta: Record<string, unknown> }) {
  const feedbackType = meta.feedbackType as string | undefined;
  const content = meta.content as string | undefined;
  const rating = meta.rating as number | undefined;
  const category = meta.category as string | undefined;

  const typeLabels: Record<string, string> = {
    resource: '资源反馈',
    general: '通用反馈',
    difficulty: '难度反馈',
    suggestion: '建议',
    bug: '问题报告',
  };

  return (
    <div className="p-3 bg-purple-50/60 border border-purple-100 rounded-xl space-y-2">
      <h4 className="text-xs font-semibold text-purple-700 flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
        反馈详情
      </h4>
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px]">
        <InfoItem label="类型" value={typeLabels[feedbackType || ''] || feedbackType || '-'} />
        {category && <InfoItem label="分类" value={category} />}
        {rating != null && <InfoItem label="评分" value={'⭐'.repeat(rating)} />}
      </div>
      {content && (
        <div className="text-[11px] text-gray-600 mt-1 p-2 bg-white/60 rounded-lg">
          {content}
        </div>
      )}
    </div>
  );
}

/* ===================================================================
 * Sub: Resource 详情
 * =================================================================== */
function ResourceDetail({ event, meta }: { event: TimelineEvent; meta: Record<string, unknown> }) {
  const resourceType = event.resourceType || (meta.type as string) || '';
  const typeLabel = RESOURCE_TYPE_LABELS[resourceType] || resourceType || '-';
  const knowledgePoints = meta.knowledgePoints as string[] | undefined;

  return (
    <div className="p-3 bg-gray-50 border border-gray-100 rounded-xl space-y-2">
      <h4 className="text-xs font-semibold text-gray-700 flex items-center gap-1.5">
        {event.event === 'resource_complete' ? (
          <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
        ) : (
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
        )}
        资源详情
      </h4>
      <div className="grid grid-cols-2 gap-2 text-[11px]">
        {event.resourceTitle && <InfoItem label="标题" value={event.resourceTitle} />}
        <InfoItem label="类型" value={typeLabel} />
        {event.relatedChapter && <InfoItem label="章节" value={event.relatedChapter} />}
        {event.relatedStageId && <InfoItem label="阶段" value={`阶段 ${event.relatedStageId.replace(/[^0-9]/g, '')}`} />}
      </div>
      {knowledgePoints && knowledgePoints.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-1">
          {knowledgePoints.map((kp, i) => (
            <span key={i} className="px-1.5 py-0.5 rounded text-[9px] bg-white border border-gray-100 text-gray-400">
              {kp}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

/* ===================================================================
 * Sub: Node / Stage 进度详情
 * =================================================================== */
function NodeProgressDetail({ event, meta }: { event: TimelineEvent; meta: Record<string, unknown> }) {
  const oldStatus = meta.oldStatus as string | undefined;
  const newStatus = meta.status as string | undefined;
  const stageTitle = meta.stageTitle as string | undefined;
  const nodeName = meta.nodeName as string | undefined;

  const statusLabel = (s: string | undefined) =>
    s === 'completed' ? '已完成' :
    s === 'in_progress' ? '学习中' :
    s === 'locked' ? '未解锁' :
    s === 'available' ? '已解锁' :
    s || '-';

  return (
    <div className="p-3 bg-rose-50/60 border border-rose-100 rounded-xl space-y-2">
      <h4 className="text-xs font-semibold text-rose-700 flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
        {event.event === 'stage_complete' ? '阶段完成' : '节点更新'}
      </h4>
      <div className="space-y-1.5 text-[11px]">
        {stageTitle && <InfoItem label="阶段名称" value={stageTitle} />}
        {nodeName && <InfoItem label="节点名称" value={nodeName} />}
        {event.relatedStageId && (
          <InfoItem label="阶段编号" value={`阶段 ${event.relatedStageId.replace(/[^0-9]/g, '')}`} />
        )}
        {(oldStatus || newStatus) && (
          <div className="flex items-center gap-2 mt-1">
            {oldStatus && (
              <span className="px-2 py-0.5 rounded text-[10px] bg-gray-200 text-gray-500 line-through">
                {statusLabel(oldStatus)}
              </span>
            )}
            {(oldStatus && newStatus) && (
              <Target className="w-3 h-3 text-gray-300" />
            )}
            {newStatus && (
              <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                newStatus === 'completed' ? 'bg-green-100 text-green-600' :
                newStatus === 'in_progress' ? 'bg-blue-100 text-blue-600' :
                'bg-gray-100 text-gray-500'
              }`}>
                {statusLabel(newStatus)}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ===================================================================
 * 通用信息条目
 * =================================================================== */
function InfoItem({ label, value }: { label: string; value: string }) {
  if (!value || value === '-' || value === '') return null;
  return (
    <div className="flex flex-col">
      <span className="text-[10px] text-gray-400">{label}</span>
      <span className="text-[11px] text-gray-700 font-medium">{value}</span>
    </div>
  );
}
