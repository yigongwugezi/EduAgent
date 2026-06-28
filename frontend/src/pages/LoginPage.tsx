import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Brain, User, Check, Trash2 } from 'lucide-react';
import { readStorageJson, writeStorageJson, runtimeStorageKeys } from '../utils/storageKeys';
import { useSubjectStore } from '../store/subjectStore';
import { useChatStore } from '../store/chatStore';
import { useProfileStore } from '../store/profileStore';

interface Learner { id: string; name: string; createdAt: number; lastLoginAt: number; }
function loadLearners(): Learner[] { return readStorageJson(runtimeStorageKeys.learners, []); }
function saveLearners(v: Learner[]) { writeStorageJson(runtimeStorageKeys.learners, v); }
function loadActive(): Learner | null { return readStorageJson(runtimeStorageKeys.activeLearner, null); }
function saveActive(v: Learner) { writeStorageJson(runtimeStorageKeys.activeLearner, v); }
function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 8); }
export function getCurrentLearner(): Learner | null { return loadActive(); }
export function logoutLearner() { try { localStorage.removeItem(runtimeStorageKeys.activeLearner.primary); } catch {} useSubjectStore.getState().load(); useChatStore.getState().reloadSession(); useProfileStore.getState().clearAll(); }

export default function LoginPage() {
  const nav = useNavigate();
  const [list, setList] = useState<Learner[]>(loadLearners);
  const [creating, setCreating] = useState(list.length === 0);
  const [name, setName] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState('');
  const active = loadActive();
  const login = (l: Learner) => { l.lastLoginAt = Date.now(); saveActive(l); saveLearners(loadLearners().map(x => x.id === l.id ? { ...x, lastLoginAt: l.lastLoginAt } : x)); useSubjectStore.getState().load(); useChatStore.getState().reloadSession(); useProfileStore.getState().clearAll(); nav('/'); };
  const create = () => { const n = name.trim(); if (!n) return; const l: Learner = { id: uid(), name: n, createdAt: Date.now(), lastLoginAt: Date.now() }; const ls = loadLearners(); ls.push(l); saveLearners(ls); saveActive(l); setList(ls); setName(''); setCreating(false); useSubjectStore.getState().load(); useChatStore.getState().reloadSession(); useProfileStore.getState().clearAll(); nav('/'); };
  const del = (id: string, e: React.MouseEvent) => { e.stopPropagation(); const ls = loadLearners().filter(x => x.id !== id); saveLearners(ls); setList(ls); if (loadActive()?.id === id) logoutLearner(); };
  const rename = (id: string) => { const n = editName.trim(); if (!n) return; const ls = loadLearners().map(x => x.id === id ? { ...x, name: n } : x); saveLearners(ls); setList(ls); const a = loadActive(); if (a?.id === id) saveActive({ ...a, name: n }); setEditingId(null); };

  return (
    <div className="min-h-screen bg-surface-50 flex items-center justify-center p-6">
      <div className="w-full max-w-sm animate-fade-in">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-r from-primary-600 to-accent-600 flex items-center justify-center mx-auto mb-4 shadow-soft">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <h1 className="font-display text-2xl font-bold text-surface-800">EduAgent</h1>
          <p className="text-surface-400 text-sm mt-1">个性化学习平台</p>
        </div>

        {active && !creating && (
          <div className="mb-5 p-4 bg-white rounded-2xl shadow-soft flex items-center gap-3 animate-fade-in">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-primary-500 to-accent-500 flex items-center justify-center text-white font-bold shadow-card">{active.name[0]}</div>
            <div className="flex-1 min-w-0"><p className="text-sm font-semibold text-surface-700">{active.name}</p><p className="text-xs text-surface-400">欢迎回来</p></div>
            <button onClick={() => nav('/')} className="px-4 py-2 bg-primary-600 text-white rounded-xl text-sm font-medium hover:bg-primary-700 transition-colors">进入</button>
          </div>
        )}

        <div className="bg-white rounded-2xl p-6 shadow-soft">
          {creating ? (
            <div className="space-y-4 animate-fade-in">
              <h2 className="font-display text-lg font-bold text-surface-800">创建学习者</h2>
              <input value={name} onChange={e => setName(e.target.value)} onKeyDown={e => e.key === 'Enter' && create()} placeholder="输入你的名字" autoFocus maxLength={20} className="w-full px-4 py-3 bg-surface-50 border border-surface-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400 transition-all" />
              <div className="flex gap-2">
                <button onClick={create} disabled={!name.trim()} className="flex-1 px-4 py-2.5 bg-primary-600 text-white rounded-xl text-sm font-semibold hover:bg-primary-700 disabled:opacity-50 transition-colors">创建并开始</button>
                {list.length > 0 && <button onClick={() => { setCreating(false); setName(''); }} className="px-4 py-2.5 text-sm text-surface-400 hover:text-surface-600">取消</button>}
              </div>
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-display text-lg font-bold text-surface-800">选择学习者</h2>
                <button onClick={() => setCreating(true)} className="text-sm font-medium text-primary-600 hover:text-primary-700">新建</button>
              </div>
              {list.length === 0 ? (
                <div className="text-center py-10"><p className="text-sm text-surface-400 mb-4">还没有学习者</p><button onClick={() => setCreating(true)} className="px-5 py-2.5 bg-primary-600 text-white rounded-xl text-sm font-medium hover:bg-primary-700 transition-colors">创建学习者</button></div>
              ) : (
                <div className="space-y-1">
                  {list.sort((a, b) => b.lastLoginAt - a.lastLoginAt).map(l => {
                    const isActive = active?.id === l.id, isEditing = editingId === l.id;
                    return (
                      <div key={l.id} onClick={() => !isEditing && login(l)} className={`flex items-center gap-3 px-3.5 py-3 rounded-xl cursor-pointer transition-all group ${isActive ? 'bg-primary-50' : 'hover:bg-surface-50'}`}>
                        <div className={`w-9 h-9 rounded-xl flex items-center justify-center text-white text-sm font-bold ${isActive ? 'bg-gradient-to-r from-primary-500 to-accent-500 shadow-card' : 'bg-surface-300 group-hover:bg-surface-400'}`}>{l.name[0]}</div>
                        {isEditing ? (
                          <div className="flex-1 flex items-center gap-2">
                            <input value={editName} onChange={e => setEditName(e.target.value)} onKeyDown={e => e.key === 'Enter' && rename(l.id)} className="flex-1 text-sm bg-white border border-surface-200 rounded-xl px-3 py-2 outline-none focus:ring-2 focus:ring-primary-200" autoFocus maxLength={20} onClick={e => e.stopPropagation()} />
                            <button onClick={e => { e.stopPropagation(); rename(l.id); }} className="p-1.5 rounded-lg text-primary-600 hover:bg-primary-50"><Check className="w-4 h-4" /></button>
                          </div>
                        ) : (
                          <div className="flex-1 min-w-0"><div className="flex items-center gap-2"><span className="text-sm font-semibold text-surface-700">{l.name}</span>{isActive && <span className="px-2 py-0.5 bg-primary-500 text-white rounded-full text-[10px] font-semibold">当前</span>}</div><p className="text-xs text-surface-400 mt-0.5">上次登录 {new Date(l.lastLoginAt).toLocaleDateString('zh-CN')}</p></div>
                        )}
                        <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
                          {!isEditing && <button onClick={e => { e.stopPropagation(); setEditingId(l.id); setEditName(l.name); }} className="p-1.5 rounded-lg hover:bg-surface-100 text-surface-400"><User className="w-3.5 h-3.5" /></button>}
                          <button onClick={e => del(l.id, e)} className="p-1.5 rounded-lg hover:bg-error-50 text-surface-400 hover:text-error-500"><Trash2 className="w-3.5 h-3.5" /></button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </>
          )}
        </div>
        <p className="text-center text-xs text-surface-300 mt-5">学习数据保存在本地浏览器</p>
      </div>
    </div>
  );
}
