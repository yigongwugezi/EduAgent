import { useEffect, useRef, useCallback } from 'react';
import { logStudyEvent } from '../api/feedback';

/**
 * 页面级学习追踪 Hook
 * 在组件 mount 时记录 page_view，unmount 时记录 page_leave 并附带停留时长
 */
export function useStudyTracker(page: string) {
  const startRef = useRef(Date.now());

  useEffect(() => {
    startRef.current = Date.now();
    logStudyEvent({
      event: 'page_view',
      metadata: { page },
    }).catch(() => { /* ignore */ });

    return () => {
      const duration = Math.round((Date.now() - startRef.current) / 1000);
      logStudyEvent({
        event: 'page_leave',
        duration,
        metadata: { page },
      }).catch(() => { /* ignore */ });
    };
  }, [page]);
}

/**
 * 快捷埋点 Hook — 返回一个 track 函数
 */
export function useTracker() {
  return useCallback((event: string, extra?: Record<string, unknown>) => {
    logStudyEvent({ event, metadata: extra }).catch(() => { /* ignore */ });
  }, []);
}
