import { Loader2, Sparkles } from 'lucide-react';

interface LoadingProps {
  text?: string;
  fullScreen?: boolean;
}

export default function Loading({ text = '加载中...', fullScreen = false }: LoadingProps) {
  const base = 'flex flex-col items-center justify-center gap-4 text-gray-400';
  return (
    <div className={`${base} ${fullScreen ? 'min-h-[60vh]' : 'py-16'}`}>
      <div className="relative">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-100 to-brand-200 flex items-center justify-center shadow-lg shadow-brand-100/50">
          <Sparkles className="w-7 h-7 text-brand-500 animate-pulse" />
        </div>
        <div className="absolute -top-1 -right-1">
          <div className="w-5 h-5 rounded-full border-2 border-brand-500 border-t-transparent animate-spin bg-white" />
        </div>
      </div>
      <div className="flex flex-col items-center gap-1">
        <span className="text-sm font-medium text-gray-500">{text}</span>
        <div className="flex items-center gap-1">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-brand-300 animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
