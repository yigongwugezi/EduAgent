import React from 'react';

/**
 * 将文本按搜索词分割，匹配部分用 <mark> 包裹实现高亮。
 * 大小写不敏感匹配，但保留原文大小写。
 *
 * @example
 *   <HighlightText text="神经网络基础" query="神经" />
 *   // → <><mark>神经</mark>网络基础</>
 */
export function HighlightText({
  text,
  query,
  className = '',
}: {
  text: string;
  query?: string;
  className?: string;
}): React.ReactElement {
  if (!query || !text) {
    return <span className={className}>{text}</span>;
  }

  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escaped})`, 'gi');
  const parts = text.split(regex);

  if (parts.length === 1) {
    // 没有匹配
    return <span className={className}>{text}</span>;
  }

  return (
    <span className={className}>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <mark
            key={i}
            className="bg-amber-200/70 text-inherit rounded-sm px-0.5"
          >
            {part}
          </mark>
        ) : (
          <React.Fragment key={i}>{part}</React.Fragment>
        ),
      )}
    </span>
  );
}

/**
 * 判断文本是否匹配搜索词（大小写不敏感）
 */
export function matchesQuery(text: string, query: string): boolean {
  if (!query || !text) return false;
  return text.toLowerCase().includes(query.toLowerCase());
}

/**
 * 从文本中提取匹配搜索词的片段摘要（用于知识标签匹配提示）
 */
export function extractMatchPreview(text: string, query: string, maxLen = 30): string | null {
  if (!query || !text) return null;
  const lowerText = text.toLowerCase();
  const lowerQuery = query.toLowerCase();
  const idx = lowerText.indexOf(lowerQuery);
  if (idx === -1) return null;

  const start = Math.max(0, idx - Math.floor((maxLen - query.length) / 2));
  const end = Math.min(text.length, idx + query.length + Math.floor((maxLen - query.length) / 2));
  let preview = text.slice(start, end);
  if (start > 0) preview = '…' + preview;
  if (end < text.length) preview = preview + '…';
  return preview;
}
