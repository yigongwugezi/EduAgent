/**
 * 统一日志工具
 *
 * 设计原则：
 * - 开发环境（import.meta.env.DEV）：输出 debug / info / warn / error
 * - 生产环境（import.meta.env.PROD）：仅输出 warn / error
 * - 所有日志携带模块标签，便于过滤
 * - 不向用户界面暴露任何调试信息
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

const isDev = import.meta.env.DEV;

const LOG_ICONS: Record<LogLevel, string> = {
  debug: '🐛',
  info: 'ℹ️',
  warn: '⚠️',
  error: '❌',
};

function formatTimestamp(): string {
  return new Date().toISOString().slice(11, 23);
}

function shouldOutput(level: LogLevel): boolean {
  if (isDev) return true;
  // 生产环境只输出 warn 和 error
  return level === 'warn' || level === 'error';
}

function log(level: LogLevel, module: string, message: string, ...args: unknown[]) {
  if (!shouldOutput(level)) return;

  const icon = LOG_ICONS[level];
  const timestamp = formatTimestamp();
  const prefix = `[${timestamp}] ${icon} [${module}]`;

  switch (level) {
    case 'debug':
      console.debug(prefix, message, ...args);
      break;
    case 'info':
      console.info(prefix, message, ...args);
      break;
    case 'warn':
      console.warn(prefix, message, ...args);
      break;
    case 'error':
      console.error(prefix, message, ...args);
      break;
  }
}

/**
 * 创建带模块标签的 Logger 实例
 *
 * @example
 * const log = createLogger('API');
 * log.debug('请求开始', { url: '/chat/stream' });
 * log.error('请求失败', err);
 */
export function createLogger(module: string) {
  return {
    debug: (message: string, ...args: unknown[]) => log('debug', module, message, ...args),
    info: (message: string, ...args: unknown[]) => log('info', module, message, ...args),
    warn: (message: string, ...args: unknown[]) => log('warn', module, message, ...args),
    error: (message: string, ...args: unknown[]) => log('error', module, message, ...args),
  };
}

// ── 全局日志级别控制 ────────────────────────────────────────────────

/**
 * 是否启用 debug 日志（仅开发环境有效）
 * 可通过 localStorage 临时覆盖：localStorage.setItem('logger_debug', 'false')
 */
export function isDebugEnabled(): boolean {
  if (!isDev) return false;
  const override = localStorage.getItem('logger_debug');
  if (override !== null) return override !== 'false';
  return true;
}
