import { AlertCircle, AlertTriangle, Inbox, RefreshCw, Sparkles, Cpu } from 'lucide-react';
import type { ReactNode } from 'react';

export type PageStateType = 'loading' | 'empty' | 'error' | 'fallback' | 'generated' | 'idle';

export function PageLoading({ text = '加载中...', overlay }: { text?: string; overlay?: boolean }) {
  const inner = (
    <div className="flex flex-col items-center gap-4 py-20">
      <div className="relative">
        <div className="w-10 h-10 rounded-full border-[3px] border-accent-100" />
        <div className="absolute inset-0 w-10 h-10 rounded-full border-[3px] border-accent-500 border-t-transparent animate-spin" />
      </div>
      <span className="text-sm text-surface-400 font-medium">{text}</span>
    </div>
  );
  if (overlay) return <div className="absolute inset-0 z-10 bg-white/60 backdrop-blur-sm flex items-center justify-center rounded-2xl">{inner}</div>;
  return inner;
}

export function PageEmpty({ icon, title, description, action }: { icon?: ReactNode; title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center py-20 text-center empty-state-glow">
      <div className="w-18 h-18 rounded-2xl bg-gradient-to-br from-gray-50 to-gray-100 border border-surface-100 flex items-center justify-center mb-6 shadow-sm">
        {icon || <Inbox className="w-9 h-9 text-surface-300" />}
      </div>
      <h3 className="text-lg font-bold text-surface-700 mb-2 tracking-tight">{title}</h3>
      {description && <p className="text-sm text-surface-400 max-w-sm mb-6 leading-relaxed">{description}</p>}
      {action}
    </div>
  );
}

export function RetryActions({ onRetry, onGoChat, chatLabel = '去对话页' }: { onRetry: () => void; onGoChat?: () => void; chatLabel?: string }) {
  return (
    <div className="flex items-center gap-3">
      <button onClick={onRetry} className="px-5 py-2.5 bg-accent-600 text-white rounded-xl text-sm font-semibold hover:bg-accent-700 transition-colors inline-flex items-center gap-2">
        <RefreshCw className="w-4 h-4" /> 重试
      </button>
      {onGoChat && <button onClick={onGoChat} className="px-5 py-2.5 bg-surface-100 text-surface-600 rounded-xl text-sm font-semibold hover:bg-surface-200 transition-colors">{chatLabel}</button>}
    </div>
  );
}

export function SourceTag({ source }: { source: string | undefined | null }) {
  if (!source || source === 'none' || source === 'user_input') return null;
  const config: Record<string, { label: string; icon: React.ReactNode; cls: string }> = {
    agent_generated: { label: 'AI 生成', icon: <Sparkles className="w-3 h-3" />, cls: 'bg-purple-50 text-purple-600' },
    system_inferred: { label: '系统推断', icon: <Cpu className="w-3 h-3" />, cls: 'bg-amber-50 text-amber-600' },
    fallback: { label: '规则兜底', icon: <Cpu className="w-3 h-3" />, cls: 'bg-slate-50 text-slate-500' },
  };
  const c = config[source];
  if (!c) return null;
  return <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium ${c.cls}`}>{c.icon}{c.label}</span>;
}

export function PageError({ title, description, onRetry, onGoChat }: { title?: string; description?: string | null; onRetry: () => void; onGoChat?: () => void }) {
  return (
    <div className="flex flex-col items-center py-20 text-center animate-fade-in-up">
      <div className="w-18 h-18 rounded-2xl bg-gradient-to-br from-red-50 to-rose-50 border border-red-100 flex items-center justify-center mb-6 shadow-sm">
        <AlertCircle className="w-9 h-9 text-red-400" />
      </div>
      <h3 className="text-lg font-bold text-surface-700 mb-2 tracking-tight">{title || '加载失败'}</h3>
      {description && <p className="text-sm text-surface-400 max-w-sm mb-6 leading-relaxed">{description}</p>}
      <RetryActions onRetry={onRetry} onGoChat={onGoChat} />
    </div>
  );
}

export function FallbackBanner({ message = '内容来自系统兜底规则。' }: { message?: string }) {
  return (
    <div className="mb-4 p-3.5 bg-amber-50/80 border border-amber-100 rounded-2xl flex items-start gap-2.5 animate-fade-in-down">
      <div className="w-7 h-7 rounded-xl bg-amber-100 flex items-center justify-center flex-shrink-0">
        <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
      </div>
      <p className="text-xs text-amber-700 leading-relaxed pt-0.5">{message}</p>
    </div>
  );
}

export function RefreshOverlay() {
  return (
    <div className="absolute inset-0 z-10 bg-white/50 backdrop-blur-[2px] flex items-center justify-center rounded-2xl animate-fade-in">
      <div className="flex items-center gap-2.5 px-4 py-2.5 bg-white rounded-xl shadow-md border border-surface-100 ring-1 ring-black/5">
        <div className="relative w-4 h-4">
          <div className="w-4 h-4 rounded-full border-2 border-accent-100" />
          <div className="absolute inset-0 w-4 h-4 rounded-full border-2 border-accent-500 border-t-transparent animate-spin" />
        </div>
        <span className="text-xs text-surface-500 font-medium">刷新中…</span>
      </div>
    </div>
  );
}
