// @ts-nocheck
import { useState, useCallback, useMemo } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Clock, Eye, CheckCircle2, FileText, Code, MessageSquare, Target, BookOpen, History, ListFilter } from 'lucide-react';
import type { TimelineEvent } from '../types/timeline';
import { timeAgo } from '../utils/format';
import { PageLoading, PageEmpty } from '../components/common/PageState';
import { useLearningEvents } from '../hooks/useLearningEvents';

const EVENT_ICON: Record<string, React.ReactNode> = { resource_view: <Eye className="w-4 h-4" />, resource_complete: <CheckCircle2 className="w-4 h-4" />, quiz_result: <FileText className="w-4 h-4" />, practice_result: <Code className="w-4 h-4" />, feedback: <MessageSquare className="w-4 h-4" />, stage_complete: <Target className="w-4 h-4" />, node_progress: <BookOpen className="w-4 h-4" /> };
const EVENT_BG: Record<string, string> = { resource_view: 'bg-blue-100 text-blue-600', resource_complete: 'bg-success-100 text-success-600', quiz_result: 'bg-warning-100 text-warning-600', practice_result: 'bg-cyan-100 text-cyan-600', feedback: 'bg-purple-100 text-purple-600', stage_complete: 'bg-rose-100 text-rose-600', node_progress: 'bg-surface-100 text-surface-500' };
const EVENT_LABEL: Record<string, string> = { resource_view: '查看资源', resource_complete: '完成资源', quiz_result: '练习', practice_result: '实操', feedback: '反馈', stage_complete: '阶段完成', node_progress: '节点进度' };
const TYPE_FILTERS = [{ v: '', l: '全部' }, { v: 'resource_view', l: '查看资源' }, { v: 'resource_complete', l: '完成资源' }, { v: 'quiz_result', l: '练习' }, { v: 'practice_result', l: '实操' }, { v: 'feedback', l: '反馈' }];

function groupByDate(events: TimelineEvent[]): [string, TimelineEvent[]][] {
  const g = new Map<string, TimelineEvent[]>();
  const today = new Date(); const todayS = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`;
  const yday = new Date(today); yday.setDate(yday.getDate()-1); const ydayS = `${yday.getFullYear()}-${String(yday.getMonth()+1).padStart(2,'0')}-${String(yday.getDate()).padStart(2,'0')}`;
  for (const e of events) {
    const d = new Date(e.timestamp); const ds = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    const l = ds === todayS ? '今天' : ds === ydayS ? '昨天' : ds;
    if (!g.has(l)) g.set(l, []); g.get(l)!.push(e);
  }
  return Array.from(g.entries());
}

export default function LearningTimelinePage() {
  const nav = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const eventType = searchParams.get('type') ?? '';
  const timeRange = searchParams.get('range') ?? '';
  const [expanded, setExpanded] = useState<string | null>(null);

  const { events, total, loading, error, refetch } = useLearningEvents(100, eventType || undefined, timeRange ? parseInt(timeRange) : undefined);
  const grouped = useMemo(() => groupByDate(events), [events]);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="font-display text-2xl font-bold text-surface-800 flex items-center gap-2"><History className="w-7 h-7 text-primary-600" />学习时间线</h2>
        <p className="text-surface-500 mt-1">共 {total} 条学习行为记录</p>
      </div>

      <div className="flex items-center gap-2 overflow-x-auto">
        {TYPE_FILTERS.map(f => { const active = eventType === f.v; return <button key={f.v} onClick={() => setSearchParams(f.v ? { type: f.v } : {}, { replace: true })} className={`px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${active ? 'bg-surface-800 text-white' : 'bg-surface-100 text-surface-500 hover:bg-surface-200'}`}>{f.l}</button>; })}
        <div className="w-px h-5 bg-surface-200 mx-1" />
        {[{v:'',l:'全部'},{v:'1',l:'今天'},{v:'7',l:'7天'},{v:'30',l:'30天'}].map(f => { const active = timeRange === f.v; return <button key={f.v} onClick={() => setSearchParams(f.v ? { type: eventType, range: f.v } : eventType ? { type: eventType } : {}, { replace: true })} className={`px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${active ? 'bg-primary-600 text-white' : 'bg-surface-100 text-surface-500 hover:bg-surface-200'}`}>{f.l}</button>; })}
      </div>

      {loading ? <PageLoading text="加载时间线…" /> :
       error ? <div className="text-center py-16"><p className="text-surface-500">{error}</p><button onClick={refetch} className="mt-3 px-4 py-2 bg-primary-600 text-white rounded-xl text-sm font-medium">重试</button></div> :
       events.length === 0 && total === 0 ? <PageEmpty icon={<History className="w-8 h-8" />} title="暂无学习行为记录" description="开始学习后这里会显示你的行为记录" /> :
       events.length === 0 ? <div className="text-center py-16"><p className="text-surface-400">当前筛选条件下没有记录</p></div> :
       <div className="space-y-6">
         {grouped.map(([label, items]) => (
           <div key={label}>
             <div className="flex items-center gap-3 mb-3"><span className="px-3 py-1 bg-surface-100 rounded-lg text-xs font-medium text-surface-500">{label}</span><div className="flex-1 h-px bg-surface-200" /><span className="text-xs text-surface-400">{items.length} 条</span></div>
             <div className="space-y-2">
               {items.map(e => {
                 const bg = EVENT_BG[e.event] || 'bg-surface-100 text-surface-500';
                 return (
                   <div key={e.id} className="bg-white rounded-xl shadow-soft hover:shadow-elevated transition-all group">
                     <div onClick={() => setExpanded(expanded===e.id?null:e.id)} className="flex items-center gap-4 p-3 cursor-pointer">
                       <div className={`w-9 h-9 rounded-xl ${bg} flex items-center justify-center flex-shrink-0`}>{EVENT_ICON[e.event] || <History className="w-4 h-4" />}</div>
                       <div className="flex-1 min-w-0"><p className="text-sm font-medium text-surface-700">{EVENT_LABEL[e.event] || e.event}{e.resourceTitle ? `: ${e.resourceTitle}` : ''}</p>{e.relatedChapter && <p className="text-xs text-surface-400 mt-0.5">{e.relatedChapter}</p>}</div>
                       <span className="text-xs text-surface-400 flex-shrink-0">{timeAgo(e.timestamp)}</span>
                       {expanded===e.id ? <ChevronUp size={14} className="text-surface-300" /> : <ChevronDown size={14} className="text-surface-300" />}
                     </div>
                     {expanded===e.id && (
                       <div className="px-4 pb-3 animate-fade-in">
                         <div className="flex items-center gap-2 pt-1 border-t border-surface-100">
                           {e.resourceId && <button onClick={() => nav(`/resources/${e.resourceId}`)} className="px-3 py-1.5 bg-primary-50 text-primary-700 rounded-lg text-[11px] font-medium hover:bg-primary-100 transition-colors">查看资源</button>}
                           {e.relatedStageId && <button onClick={() => nav(`/path?stage=${e.relatedStageId}`)} className="px-3 py-1.5 bg-surface-100 text-surface-600 rounded-lg text-[11px] font-medium hover:bg-surface-200 transition-colors">跳转阶段</button>}
                         </div>
                       </div>
                     )}
                   </div>
                 );
               })}
             </div>
           </div>
         ))}
       </div>
      }
    </div>
  );
}
