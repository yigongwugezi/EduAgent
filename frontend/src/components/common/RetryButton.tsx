import { RefreshCw } from 'lucide-react';

interface RetryButtonProps {
  onClick: () => void;
  label?: string;
  size?: 'sm' | 'md';
  variant?: 'default' | 'ghost';
}

/** 统一重试按钮 */
export default function RetryButton({
  onClick,
  label = '重试',
  size = 'md',
  variant = 'default',
}: RetryButtonProps) {
  const base = 'inline-flex items-center gap-1.5 rounded-xl font-semibold transition-all';
  const sizeClass = size === 'sm' ? 'px-3 py-1.5 text-xs' : 'px-5 py-2.5 text-sm';
  const variantClass = variant === 'ghost'
    ? 'bg-red-50 text-red-600 hover:bg-red-100 border border-red-100'
    : 'bg-gray-900 text-white hover:bg-gray-800';

  return (
    <button onClick={onClick} className={`${base} ${sizeClass} ${variantClass}`}>
      <RefreshCw className="w-4 h-4" />
      {label}
    </button>
  );
}
