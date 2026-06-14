import { useCallback, useEffect, useRef, useState } from 'react';
import { useProfileStore } from '../store/profileStore';
import { useChatStore } from '../store/chatStore';
import * as profileApi from '../api/profile';
import type { StudentProfile } from '../types/profile';

export function useProfile() {
  const store = useProfileStore();
  const currentSessionId = useChatStore((state) => state.currentSessionId);
  const [loading, setLoading] = useState(false);
  const fetchedSessionRef = useRef<string | null>(null);

  const fetchProfile = useCallback(async () => {
    setLoading(true);
    store.setLoading(true);
    try {
      const res = await profileApi.getProfile(currentSessionId);
      if (res?.profile) {
        store.setProfile(res.profile);
      }
    } catch {
      store.setError('加载画像失败，请稍后重试');
    } finally {
      setLoading(false);
      store.setLoading(false);
    }
  }, [currentSessionId, store]);

  const buildProfile = useCallback(
    async (message: string): Promise<StudentProfile | null> => {
      setLoading(true);
      try {
        const res = await profileApi.buildProfile({ message, sessionId: currentSessionId });
        if (res?.profile) {
          store.setProfile(res.profile);
        }
        return res?.profile || null;
      } catch {
        store.setError('画像构建失败');
        return null;
      } finally {
        setLoading(false);
      }
    },
    [currentSessionId, store],
  );

  useEffect(() => {
    if (fetchedSessionRef.current !== currentSessionId) {
      fetchedSessionRef.current = currentSessionId;
      fetchProfile();
    }
  }, [currentSessionId, fetchProfile]);

  return { ...store, loading, fetchProfile, buildProfile };
}
