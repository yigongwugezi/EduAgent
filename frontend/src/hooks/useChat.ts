import { useCallback, useEffect, useState } from 'react';
import { useChatStore } from '../store/chatStore';
import * as chatApi from '../api/chat';
import { createLogger } from '../utils/logger';

const log = createLogger('Chat');

export function useChat() {
  const store = useChatStore();
  const [loading, setLoading] = useState(false);

  const loadSessions = useCallback(async () => {
    setLoading(true);
    try {
      const res = await chatApi.getSessions();
      store.setSessions(res.sessions);
      log.debug(`已加载 ${res.sessions.length} 个会话`);
    } catch (err) {
      log.warn('加载会话列表失败', err instanceof Error ? err.message : err);
    } finally {
      setLoading(false);
    }
  }, [store]);

  const loadMessages = useCallback(
    async (sessionId: string) => {
      setLoading(true);
      try {
        const res = await chatApi.getSessionMessages(sessionId);
        store.clearMessages();
        res.messages.forEach((m) => store.addMessage(m));
      } finally {
        setLoading(false);
      }
    },
    [store],
  );

  const deleteSession = useCallback(
    async (id: string) => {
      await chatApi.deleteSession(id);
      store.setSessions(store.sessions.filter((s) => s.id !== id));
    },
    [store],
  );

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  return { ...store, loading, loadSessions, loadMessages, deleteSession };
}
