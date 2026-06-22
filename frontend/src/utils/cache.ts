/**
 * 本地缓存策略工具
 *
 * 职责：
 * - 统一管理清除缓存逻辑（保留必要数据）
 * - 统一管理导入/导出逻辑
 * - 跨组件复用，避免重复代码
 */

import { runtimeStorageKeys, readStorageItem } from './storageKeys';

/**
 * 安全清除本地缓存
 *
 * 清除所有 localStorage 数据，但保留学习者身份信息，
 * 确保清除后系统仍能恢复，用户不会丢失账号。
 *
 * 保留的 key:
 * - r436_runtime_learners          — 学习者列表
 * - r436_runtime_active_learner    — 当前活跃学习者
 * - r436_runtime_learning_preferences — 学习偏好
 * - edu_token                      — 认证 token
 */
export function safeClearCache(): void {
  // 先读取需要保留的数据
  const learners = readStorageItem(runtimeStorageKeys.learners);
  const activeLearner = readStorageItem(runtimeStorageKeys.activeLearner);
  const prefs = readStorageItem(runtimeStorageKeys.learningPrefs);
  let token: string | null = null;
  try {
    token = localStorage.getItem(runtimeStorageKeys.authToken.primary);
  } catch {
    // noop
  }

  // 清除全部
  localStorage.clear();

  // 恢复必要数据
  if (learners) localStorage.setItem(runtimeStorageKeys.learners.primary, learners);
  if (activeLearner) localStorage.setItem(runtimeStorageKeys.activeLearner.primary, activeLearner);
  if (prefs) localStorage.setItem(runtimeStorageKeys.learningPrefs.primary, prefs);
  if (token) localStorage.setItem(runtimeStorageKeys.authToken.primary, token);
}

/**
 * 导出全部数据到 JSON
 */
export function exportAllData(): Record<string, unknown> {
  const data: Record<string, unknown> = {};
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key) {
      try {
        data[key] = JSON.parse(localStorage.getItem(key) || '');
      } catch {
        data[key] = localStorage.getItem(key);
      }
    }
  }
  return data;
}

/**
 * 从 JSON 对象导入数据到 localStorage
 * 会覆盖同名 key 的数据
 */
export function importAllData(data: Record<string, unknown>): void {
  Object.entries(data).forEach(([key, value]) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // 忽略无法序列化的值
    }
  });
}

/**
 * 清除所有科目相关的缓存数据（保留学习者信息）
 * 用于科目切换时的缓存清理
 */
export function clearSubjectCache(): void {
  const prefix = 'r436_runtime_';
  const keysToRemove: string[] = [];
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key?.startsWith(prefix)) {
      // 保留学习者相关的 key
      if (
        key.startsWith(`${prefix}learners`) ||
        key.startsWith(`${prefix}active_learner`) ||
        key.startsWith(`${prefix}learning_preferences`)
      ) {
        continue;
      }
      keysToRemove.push(key);
    }
  }
  keysToRemove.forEach((key) => localStorage.removeItem(key));
}

/**
 * 计算 localStorage 总大小（字节）
 */
export function getCacheSize(): number {
  let size = 0;
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key) {
      size += key.length * 2; // key 的字节数（UTF-16）
      size += (localStorage.getItem(key)?.length || 0) * 2; // value 的字节数
    }
  }
  return size;
}

/**
 * 格式化字节数为人类可读字符串
 */
export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
