import { useCallback, useEffect, useState } from 'react';
import * as knowledgeApi from '../api/knowledge';
import { useChatStore } from '../store/chatStore';
import type { LearningPath } from '../types/learningPath';

export function useLearningPath() {
  const currentSessionId = useChatStore((state) => state.currentSessionId);
  const [path, setPath] = useState<LearningPath | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchPath = useCallback(async () => {
    setLoading(true);
    try {
      const res = await knowledgeApi.getLearningPath(currentSessionId);
      setPath(res.path);
    } finally {
      setLoading(false);
    }
  }, [currentSessionId]);

  const generatePath = useCallback(async (params: { sessionId?: string; targetTopics?: string[] }) => {
    setLoading(true);
    try {
      const res = await knowledgeApi.generateLearningPath({ ...params, sessionId: params.sessionId || currentSessionId });
      setPath(res.path);
      return res.path;
    } finally {
      setLoading(false);
    }
  }, [currentSessionId]);

  const updateNode = useCallback(async (nodeId: string, mastery: number) => {
    await knowledgeApi.updateNodeProgress(nodeId, mastery, currentSessionId);
    if (!path) return;
    setPath({
      ...path,
      stages: path.stages.map((s) => ({
        ...s,
        nodes: s.nodes.map((n) => (n.id === nodeId ? { ...n, mastery } : n)),
      })),
    });
  }, [currentSessionId, path]);

  useEffect(() => { fetchPath(); }, [fetchPath]);

  return { path, loading, fetchPath, generatePath, updateNode };
}
