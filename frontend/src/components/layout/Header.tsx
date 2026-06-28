import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Search, Calendar, TrendingUp } from 'lucide-react';
import { getCurrentLearner } from '../../pages/LoginPage';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export default function Header({ title, subtitle }: HeaderProps) {
  const nav = useNavigate();
  const user = getCurrentLearner();
  const [q, setQ] = useState('');
  const handleSearch = (e: React.KeyboardEvent) => { if (e.key === 'Enter' && q.trim()) { nav(`/resources?search=${encodeURIComponent(q.trim())}`); } };
  return (
    <div className="bg-white border-b border-surface-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-surface-800">{title}</h1>
          {subtitle && <p className="text-surface-500 text-sm mt-1">{subtitle}</p>}
        </div>

        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
            <input type="text" value={q} onChange={e => setQ(e.target.value)} onKeyDown={handleSearch} placeholder="搜索学习资源..." className="w-64 pl-10 pr-4 py-2.5 bg-surface-50 border border-surface-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400 transition-all" />
          </div>

          <div className="flex items-center gap-6 px-4 border-l border-r border-surface-200">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-accent-50 flex items-center justify-center">
                <TrendingUp size={16} className="text-accent-600" />
              </div>
              <div>
                <p className="text-xs text-surface-400">连续学习</p>
                <p className="text-sm font-semibold text-surface-700">7天</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-warning-50 flex items-center justify-center">
                <Calendar size={16} className="text-warning-600" />
              </div>
              <div>
                <p className="text-xs text-surface-400">今日时长</p>
                <p className="text-sm font-semibold text-surface-700">2.5h</p>
              </div>
            </div>
          </div>

          <button className="relative w-10 h-10 rounded-xl bg-surface-50 hover:bg-surface-100 flex items-center justify-center transition-colors">
            <Bell size={20} className="text-surface-600" />
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-error-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
              3
            </span>
          </button>

          <div onClick={() => nav('/profile')} className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-white font-semibold cursor-pointer hover:shadow-lg transition-shadow">
            {user?.name?.charAt(0) || '?'}
          </div>
        </div>
      </div>
    </div>
  );
}
