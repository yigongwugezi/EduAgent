import type { ReactNode } from 'react';

interface BaseCardProps {
  children: ReactNode;
  className?: string;
  padding?: 'sm' | 'md' | 'lg';
  hover?: boolean;
  onClick?: () => void;
}

const PADDING = { sm: 'p-4', md: 'p-5', lg: 'p-6' };

/** 统一卡片容器 — 白底、圆角、微妙阴影，支持悬停抬起 */
export default function BaseCard({
  children,
  className = '',
  padding = 'md',
  hover = false,
  onClick,
}: BaseCardProps) {
  return (
    <div
      onClick={onClick}
      className={[
        'bg-white border border-surface-100/80 rounded-2xl shadow-sm',
        hover ? 'hover:shadow-md hover:-translate-y-0.5 transition-all duration-200' : '',
        PADDING[padding],
        onClick ? 'cursor-pointer' : '',
        className,
      ].join(' ')}
    >
      {children}
    </div>
  );
}
