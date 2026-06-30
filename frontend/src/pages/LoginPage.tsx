import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Brain, Eye, EyeOff, User } from 'lucide-react';
import { useAuthStore, getLegacyLearner } from '../store/authStore';

export { getLegacyLearner };

export default function LoginPage() {
  const nav = useNavigate();
  const auth = useAuthStore();

  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [nickname, setNickname] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const trimPhone = phone.replace(/\s/g, '');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!trimPhone || trimPhone.length < 11) { setError('请输入正确手机号'); return; }
    if (!password || password.length < 6) { setError('密码至少6位'); return; }
    if (mode === 'register' && !nickname.trim()) { setError('请输入昵称'); return; }

    setLoading(true);
    try {
      if (mode === 'login') {
        await auth.login(trimPhone, password);
      } else {
        await auth.register({ phone: trimPhone, password, nickname: nickname.trim() || '学习者' });
      }
      nav('/');
    } catch (err: any) {
      setError(err?.message || (mode === 'login' ? '登录失败' : '注册失败'));
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setMode(m => m === 'login' ? 'register' : 'login');
    setError('');
  };

  const legacy = getLegacyLearner();

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-900 flex items-center justify-center p-6">
      <div className="w-full max-w-sm animate-fade-in">
        {/* ── Logo ── */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-r from-primary-600 to-accent-600 flex items-center justify-center mx-auto mb-4 shadow-soft">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <h1 className="font-display text-2xl font-bold text-surface-800 dark:text-gray-100">EduAgent</h1>
          <p className="text-surface-400 dark:text-gray-500 text-sm mt-1">AI 个性化学习平台</p>
        </div>

        {/* ── Card ── */}
        <div className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-soft">
          <h2 className="font-display text-lg font-bold text-surface-800 dark:text-gray-100 mb-5">
            {mode === 'login' ? '登录' : '注册'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Phone */}
            <div>
              <label className="text-xs font-medium text-surface-500 dark:text-gray-400 mb-1 block">手机号</label>
              <input
                type="tel" value={phone} maxLength={13}
                onChange={e => setPhone(e.target.value.replace(/\D/g, '').replace(/(\d{3})(\d{4})(\d{0,4})/, (_, a, b, c) => c ? `${a} ${b} ${c}` : b ? `${a} ${b}` : a))}
                placeholder="138 0000 0000"
                className="w-full px-4 py-3 bg-surface-50 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-500/30 dark:text-gray-100 transition-all"
              />
            </div>

            {/* Password */}
            <div>
              <label className="text-xs font-medium text-surface-500 dark:text-gray-400 mb-1 block">密码</label>
              <div className="relative">
                <input
                  type={showPwd ? 'text' : 'password'} value={password} maxLength={128}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="至少6位"
                  className="w-full px-4 py-3 pr-10 bg-surface-50 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-500/30 dark:text-gray-100 transition-all"
                />
                <button type="button" onClick={() => setShowPwd(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-surface-600 dark:hover:text-gray-300">
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* Nickname (register only) */}
            {mode === 'register' && (
              <div>
                <label className="text-xs font-medium text-surface-500 dark:text-gray-400 mb-1 block">昵称</label>
                <div className="relative">
                  <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" />
                  <input
                    type="text" value={nickname} maxLength={20}
                    onChange={e => setNickname(e.target.value)}
                    placeholder="你的称呼"
                    className="w-full pl-10 pr-4 py-3 bg-surface-50 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-500/30 dark:text-gray-100 transition-all"
                  />
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <p className="text-sm text-error-500 bg-error-50 dark:bg-error-500/10 rounded-lg px-3 py-2">{error}</p>
            )}

            {/* Submit */}
            <button type="submit" disabled={loading}
              className="w-full py-3 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-xl text-sm font-semibold transition-colors">
              {loading ? '处理中...' : mode === 'login' ? '登录' : '注册并开始'}
            </button>
          </form>

          {/* Switch mode */}
          <p className="text-center text-sm text-surface-400 dark:text-gray-500 mt-4">
            {mode === 'login' ? '还没有账号？' : '已有账号？'}
            <button onClick={switchMode} className="ml-1 text-primary-600 hover:text-primary-700 font-medium">
              {mode === 'login' ? '立即注册' : '去登录'}
            </button>
          </p>

          {/* Legacy migration hint */}
          {legacy && mode === 'login' && (
            <div className="mt-4 p-3 bg-warning-50 dark:bg-warning-500/10 rounded-xl border border-warning-200 dark:border-warning-500/20">
              <p className="text-xs text-warning-700 dark:text-warning-400">
                检测到本地学习数据（{legacy.name}）。登录后可在设置中迁移到新账号。
              </p>
            </div>
          )}
        </div>

        <p className="text-center text-xs text-surface-300 dark:text-gray-600 mt-5">
          首次使用请先注册
        </p>
      </div>
    </div>
  );
}
