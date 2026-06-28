import { Info, ShieldAlert } from 'lucide-react';
import type { ProfileDimension } from '../../types/profile';
import ExpandableText from '../common/ExpandableText';

const SRC: Record<string, string> = {
  user_input: '用户提供', inferred: '系统推断', llm_generated: '大模型生成',
  rule_based_fallback: '规则兜底', diagnosis: '诊断分析', feedback: '用户反馈',
};

export default function ProfileDimensionCard({ dim }: { dim: ProfileDimension; index: number }) {
  const label = SRC[dim.source];
  return (
    <div className="bg-white border border-n-200 rounded-2xl p-5 hover:border-teal-200 hover:shadow-md transition-all duration-300 group">
      <div className="flex items-start justify-between mb-3">
        <h4 className="text-sm font-bold text-n-900">{dim.label}</h4>
        {label && <span className="text-[10px] text-n-400 bg-n-50 px-2 py-0.5 rounded-full">{label}</span>}
      </div>

      <div className="flex items-center gap-3 mb-3">
        <div className="flex-1 h-2.5 bg-n-100 rounded-full overflow-hidden">
          <div className="h-full bg-teal-600 rounded-full transition-all duration-700" style={{ width: `${dim.score}%` }} />
        </div>
        <span className="text-xl font-extrabold text-teal-700 tabular-nums">{dim.score}</span>
      </div>

      {dim.value && <p className="text-xs text-n-600 leading-relaxed mb-2">{dim.value}</p>}
      {(dim.explanation || dim.description) && (
        <ExpandableText text={dim.explanation || dim.description || ''} maxLines={3} className="text-xs text-n-500 leading-relaxed mb-2" />
      )}

      {dim.evidence && (
        <div className="mb-2 p-3 bg-warm-50 border border-warm-100 rounded-xl">
          <div className="flex items-center gap-1.5 mb-1.5"><Info className="w-3 h-3 text-warm-400" /><span className="text-[10px] font-bold text-n-400 uppercase tracking-wider">支撑证据</span></div>
          <ExpandableText text={dim.evidence} maxLines={4} className="text-[11px] text-n-500 leading-relaxed" />
        </div>
      )}

      <div className="flex items-center gap-1.5 text-[10px] text-n-400">
        <div className="flex-1 h-1 bg-n-100 rounded-full overflow-hidden">
          <div className="h-full bg-teal-300 rounded-full" style={{ width: `${dim.confidence * 100}%` }} />
        </div>
        {dim.confidence < 0.5 ? (
          <span className="tabular-nums text-warm-400 flex items-center gap-0.5 font-medium"><ShieldAlert className="w-2.5 h-2.5" />需更多数据</span>
        ) : <span className="tabular-nums">{(dim.confidence * 100).toFixed(0)}%</span>}
      </div>
      {dim.confidence < 0.5 && dim.source !== 'user_input' && (
        <div className="mt-2 p-2.5 bg-warm-50 border border-warm-100 rounded-xl">
          <p className="text-[10px] text-n-600 leading-relaxed">此维度基于有限数据推断（置信度 {(dim.confidence * 100).toFixed(0)}%），继续学习后可获得更精准的画像。</p>
        </div>
      )}
    </div>
  );
}
