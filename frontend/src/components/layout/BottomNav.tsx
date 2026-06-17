import { useNavigate, useLocation } from 'react-router-dom';
import { Home, MessageSquare, Library, GitFork, User, TrendingUp } from 'lucide-react';

const tabs = [
  { path: '/', label: '首页', icon: Home },
  { path: '/chat', label: '对话', icon: MessageSquare },
  { path: '/resources', label: '资源库', icon: Library },
  { path: '/path', label: '路径', icon: GitFork },
  { path: '/profile', label: '画像', icon: User },
  { path: '/analytics', label: '分析', icon: TrendingUp },
];

export default function BottomNav() {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  return (
    <nav className="bg-white/90 backdrop-blur-2xl border-t border-gray-100 sticky bottom-0 z-50 md:hidden safe-area-bottom shadow-[0_-4px_20px_rgba(0,0,0,0.04)]">
      <div className="flex items-center justify-around h-16 px-1">
        {tabs.map(({ path, label, icon: Icon }) => {
          const active = pathname === path;
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className={`relative flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-xl transition-all duration-200 min-w-[52px] group ${
                active ? 'text-brand-600' : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              {active && (
                <div className="absolute -top-0.5 left-1/2 -translate-x-1/2 w-6 h-0.5 bg-brand-500 rounded-full animate-fade-in-up" />
              )}
              <div className={`p-1.5 rounded-xl transition-all duration-300 ${
                active
                  ? 'bg-brand-50 scale-110'
                  : 'group-hover:bg-gray-50 group-hover:scale-105'
              }`}>
                <Icon className={`w-[18px] h-[18px] transition-transform duration-300 ${
                  active ? 'scale-110' : ''
                }`} />
              </div>
              <span className={`text-[10px] font-semibold transition-all duration-300 ${
                active ? 'opacity-100 translate-y-0' : 'opacity-60'
              }`}>{label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
