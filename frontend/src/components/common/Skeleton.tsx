/* ===================================================================
 * 骨架屏组件 — 用于数据加载时的占位
 * =================================================================== */

export function SkeletonCard() {
  return (
    <div className="bg-white border border-gray-100 rounded-2xl p-5 animate-pulse">
      <div className="flex items-start gap-3 mb-3">
        <div className="w-10 h-10 rounded-xl bg-gray-100 flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-gray-100 rounded-lg w-3/4" />
          <div className="h-3 bg-gray-50 rounded-lg w-full" />
        </div>
      </div>
      <div className="flex gap-2 mb-3">
        <div className="h-5 bg-gray-50 rounded-md w-14" />
        <div className="h-5 bg-gray-50 rounded-md w-20" />
      </div>
      <div className="h-3 bg-gray-50 rounded-lg w-1/3" />
    </div>
  );
}

export function SkeletonLine({ width = '100%' }: { width?: string }) {
  return (
    <div className="h-4 bg-gray-100 rounded-lg animate-pulse" style={{ width }} />
  );
}

export function SkeletonAvatar({ size = 'w-10 h-10' }: { size?: string }) {
  return (
    <div className={`${size} rounded-xl bg-gray-100 animate-pulse flex-shrink-0`} />
  );
}
