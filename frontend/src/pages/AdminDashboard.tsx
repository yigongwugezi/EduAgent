import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Database, GitGraph, BarChart3, Settings, Activity,
  Plus, Edit3, Trash2, Upload, Download, CheckCircle, XCircle, Search, ChevronDown, Filter,
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import * as adminApi from '../api/admin';
import type { AdminQuestion, AdminKP, ConfigItem, GraphData } from '../api/admin';

const TABS = [
  { id: 'questions', label: '题库管理', icon: Database },
  { id: 'knowledge', label: '知识图谱', icon: GitGraph },
  { id: 'stats', label: '数据统计', icon: BarChart3 },
  { id: 'config', label: '系统配置', icon: Settings },
  { id: 'monitor', label: '模型监控', icon: Activity },
] as const;

const QUESTION_TYPES = ['choice', 'fill', 'truefalse', 'shortanswer'];
const TYPE_LABELS: Record<string, string> = { choice: '选择题', fill: '填空题', truefalse: '判断题', shortanswer: '解答题' };
const DIFF_LABELS: Record<string, string> = { easy: '简单', medium: '中等', hard: '困难', challenge: '挑战' };
const STATUS_LABELS: Record<string, string> = { draft: '草稿', published: '已发布', archived: '已归档' };

function AdminGuard({ children }: { children: React.ReactNode }) {
  const role = useAuthStore(s => s.learner?.role);
  const nav = useNavigate();
  useEffect(() => { if (role && !['admin', 'teacher'].includes(role)) nav('/'); }, [role, nav]);
  if (!role || !['admin', 'teacher'].includes(role)) return null;
  return <>{children}</>;
}

export default function AdminDashboard() {
  const [tab, setTab] = useState('questions');

  return (
    <AdminGuard>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h2 className="font-display text-2xl font-bold text-surface-800 dark:text-gray-100">后台管理</h2>
          <p className="text-surface-500 dark:text-gray-400 mt-1">题库 · 知识图谱 · 数据统计 · 系统配置</p>
        </div>

        <div className="flex gap-6">
          {/* Left nav */}
          <div className="w-44 flex-shrink-0">
            <nav className="bg-white dark:bg-surface-700 rounded-2xl p-2 shadow-soft space-y-0.5 sticky top-24">
              {TABS.map(t => (
                <button key={t.id} onClick={() => setTab(t.id)}
                  className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-left transition-all text-sm ${
                    tab === t.id ? 'bg-brand-500/10 dark:bg-brand-500/20 text-brand-600 dark:text-brand-400 font-medium' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-surface-600'
                  }`}>
                  <t.icon size={16} />{t.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Right content */}
          <div className="flex-1 min-w-0 bg-white dark:bg-surface-700 rounded-2xl p-6 shadow-soft">
            {tab === 'questions' && <QuestionsTab />}
            {tab === 'knowledge' && <KnowledgeTab />}
            {tab === 'stats' && <StatsTab />}
            {tab === 'config' && <ConfigTab />}
            {tab === 'monitor' && <MonitorTab />}
          </div>
        </div>
      </div>
    </AdminGuard>
  );
}

/* ===================================================================
 * Tab: Questions
 * =================================================================== */
function QuestionsTab() {
  const [questions, setQuestions] = useState<AdminQuestion[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({ subject: '', type: '', difficulty: '', status: 'published', search: '' });
  const [editing, setEditing] = useState<AdminQuestion | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [importing, setImporting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminApi.listQuestions({ ...filters, page, page_size: 20 });
      setQuestions(res.questions);
      setTotal(res.pagination.total);
    } catch { /* noop */ }
    setLoading(false);
  }, [filters, page]);

  useEffect(() => { load(); }, [load]);

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      const text = await file.text();
      try {
        const items = JSON.parse(text);
        const res = await adminApi.batchImport(Array.isArray(items) ? items : [items]);
        alert(`导入成功：${res.imported} 题`);
        load();
      } catch { alert('JSON 格式错误'); }
    };
    input.click();
  };

  const handleExport = async () => {
    const res = await adminApi.exportQuestions(filters.subject);
    const blob = new Blob([JSON.stringify(res.questions, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `questions_${new Date().toISOString().slice(0,10)}.json`; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-lg font-semibold text-gray-800 dark:text-gray-100">题库管理</h3>
        <div className="flex gap-2">
          <button onClick={handleImport} className="flex items-center gap-1.5 px-3 py-2 bg-gray-50 dark:bg-surface-600 border border-gray-200 dark:border-gray-500 rounded-lg text-xs font-medium hover:bg-gray-100 dark:hover:bg-surface-500 transition-colors"><Upload size={14} />批量导入</button>
          <button onClick={handleExport} className="flex items-center gap-1.5 px-3 py-2 bg-gray-50 dark:bg-surface-600 border border-gray-200 dark:border-gray-500 rounded-lg text-xs font-medium hover:bg-gray-100 dark:hover:bg-surface-500 transition-colors"><Download size={14} />导出</button>
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-1.5 px-3 py-2 bg-brand-500 text-white rounded-lg text-xs font-medium hover:bg-brand-600 transition-colors"><Plus size={14} />新建题目</button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <input placeholder="搜索题目内容..." value={filters.search} onChange={e => { setFilters(f => ({ ...f, search: e.target.value })); setPage(1); }}
          className="px-3 py-2 bg-gray-50 dark:bg-surface-600 border border-gray-200 dark:border-gray-500 rounded-lg text-xs w-48" />
        <SelectSm value={filters.subject} onChange={v => { setFilters(f => ({ ...f, subject: v })); setPage(1); }} options={[
          { value: '', label: '全部学科' }, { value: '高中数学', label: '高中数学' }, { value: '高中物理', label: '高中物理' }, { value: '高中英语', label: '高中英语' },
        ]} />
        <SelectSm value={filters.type} onChange={v => { setFilters(f => ({ ...f, type: v })); setPage(1); }} options={[
          { value: '', label: '全部题型' }, ...QUESTION_TYPES.map(t => ({ value: t, label: TYPE_LABELS[t] })),
        ]} />
        <SelectSm value={filters.difficulty} onChange={v => { setFilters(f => ({ ...f, difficulty: v })); setPage(1); }} options={[
          { value: '', label: '全部难度' }, { value: 'easy', label: '简单' }, { value: 'medium', label: '中等' }, { value: 'hard', label: '困难' }, { value: 'challenge', label: '挑战' },
        ]} />
        <SelectSm value={filters.status} onChange={v => { setFilters(f => ({ ...f, status: v })); setPage(1); }} options={[
          { value: 'published', label: '已发布' }, { value: 'draft', label: '草稿' }, { value: 'archived', label: '已归档' },
        ]} />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 dark:border-gray-600 text-left">
              <th className="pb-2 font-medium text-gray-500 dark:text-gray-400 w-16">题型</th>
              <th className="pb-2 font-medium text-gray-500 dark:text-gray-400">内容</th>
              <th className="pb-2 font-medium text-gray-500 dark:text-gray-400 w-16">难度</th>
              <th className="pb-2 font-medium text-gray-500 dark:text-gray-400 w-16">状态</th>
              <th className="pb-2 font-medium text-gray-500 dark:text-gray-400 w-20">操作</th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan={5} className="py-8 text-center text-gray-400">加载中...</td></tr>}
            {!loading && questions.length === 0 && <tr><td colSpan={5} className="py-8 text-center text-gray-400">暂无题目</td></tr>}
            {questions.map(q => (
              <tr key={q.id} className="border-b border-gray-50 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-surface-600 transition-colors">
                <td className="py-2.5 text-xs text-gray-500">{TYPE_LABELS[q.type] || q.type}</td>
                <td className="py-2.5">
                  <div className="text-gray-700 dark:text-gray-200 truncate max-w-xs">{q.content?.stem as string || '(空)'}</div>
                  <div className="text-xs text-gray-400 mt-0.5">{q.knowledge_point} · {q.subject}</div>
                </td>
                <td className="py-2.5"><span className={`text-xs px-2 py-0.5 rounded-full font-medium ${q.difficulty === 'easy' ? 'bg-green-100 text-green-700 dark:bg-green-500/10 dark:text-green-400' : q.difficulty === 'hard' ? 'bg-orange-100 text-orange-700 dark:bg-orange-500/10 dark:text-orange-400' : 'bg-blue-100 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400'}`}>{DIFF_LABELS[q.difficulty] || q.difficulty}</span></td>
                <td className="py-2.5"><span className={`text-xs ${q.status === 'published' ? 'text-green-600' : q.status === 'draft' ? 'text-yellow-600' : 'text-gray-400'}`}>{STATUS_LABELS[q.status] || q.status}</span></td>
                <td className="py-2.5">
                  <div className="flex gap-1">
                    <button onClick={() => setEditing(q)} className="p-1 rounded hover:bg-gray-100 dark:hover:bg-surface-500 text-gray-400 hover:text-gray-600"><Edit3 size={13} /></button>
                    <button onClick={async () => { await adminApi.deleteQuestion(q.id); load(); }} className="p-1 rounded hover:bg-red-50 dark:hover:bg-red-500/10 text-gray-400 hover:text-red-500"><Trash2 size={13} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {total > 20 && (
        <div className="flex items-center justify-between text-xs text-gray-500 pt-2">
          <span>共 {total} 题</span>
          <div className="flex gap-1">
            <button onClick={() => setPage(p => Math.max(1, p-1))} disabled={page <= 1} className="px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-surface-600 disabled:opacity-30">上一页</button>
            <span className="px-2 py-1">{page} / {Math.ceil(total / 20)}</span>
            <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(total / 20)} className="px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-surface-600 disabled:opacity-30">下一页</button>
          </div>
        </div>
      )}

      {/* Edit modal */}
      {editing && <QuestionEditModal question={editing} onClose={() => setEditing(null)} onSaved={() => { setEditing(null); load(); }} />}
      {/* Create modal */}
      {showCreate && <QuestionEditModal onClose={() => setShowCreate(false)} onSaved={() => { setShowCreate(false); load(); }} />}
    </div>
  );
}

function QuestionEditModal({ question, onClose, onSaved }: { question?: AdminQuestion; onClose: () => void; onSaved: () => void }) {
  const [stem, setStem] = useState(question?.content?.stem as string || '');
  const [answer, setAnswer] = useState(question?.content?.answer as string || '');
  const [explanation, setExplanation] = useState(question?.content?.explanation as string || '');
  const [subject, setSubject] = useState(question?.subject || '');
  const [kp, setKp] = useState(question?.knowledge_point || '');
  const [type, setType] = useState(question?.type || 'choice');
  const [difficulty, setDifficulty] = useState(question?.difficulty || 'medium');
  const [saving, setSaving] = useState(false);

  const save = async () => {
    setSaving(true);
    const content = { stem, answer, explanation };
    try {
      if (question) {
        await adminApi.updateQuestion(question.id, { subject, knowledge_point: kp, type, difficulty, content });
      } else {
        await adminApi.createQuestion({ subject, knowledge_point: kp, type, difficulty, content });
      }
      onSaved();
    } catch (e: any) { alert(e?.message || '保存失败'); }
    setSaving(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={onClose}>
      <div className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-elevated w-full max-w-lg max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <h3 className="font-display text-lg font-semibold mb-4">{question ? '编辑题目' : '新建题目'}</h3>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div><label className="text-xs text-gray-500 mb-1 block">学科</label><input value={subject} onChange={e => setSubject(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm" /></div>
            <div><label className="text-xs text-gray-500 mb-1 block">知识点</label><input value={kp} onChange={e => setKp(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm" /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="text-xs text-gray-500 mb-1 block">题型</label>
              <select value={type} onChange={e => setType(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm">
                {QUESTION_TYPES.map(t => <option key={t} value={t}>{TYPE_LABELS[t]}</option>)}
              </select>
            </div>
            <div><label className="text-xs text-gray-500 mb-1 block">难度</label>
              <select value={difficulty} onChange={e => setDifficulty(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm">
                {['easy','medium','hard','challenge'].map(d => <option key={d} value={d}>{DIFF_LABELS[d]}</option>)}
              </select>
            </div>
          </div>
          <div><label className="text-xs text-gray-500 mb-1 block">题目内容</label><textarea value={stem} onChange={e => setStem(e.target.value)} rows={3} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm resize-none" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">答案</label><input value={answer} onChange={e => setAnswer(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">解析</label><textarea value={explanation} onChange={e => setExplanation(e.target.value)} rows={2} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm resize-none" /></div>
        </div>
        <div className="flex justify-end gap-2 mt-5">
          <button onClick={onClose} className="px-4 py-2 text-sm text-gray-500 hover:bg-gray-100 dark:hover:bg-surface-600 rounded-lg">取消</button>
          <button onClick={save} disabled={saving} className="px-4 py-2 bg-brand-500 text-white text-sm rounded-lg hover:bg-brand-600 disabled:opacity-50">{saving ? '保存中...' : '保存'}</button>
        </div>
      </div>
    </div>
  );
}

/* ===================================================================
 * Tab: Knowledge Graph
 * =================================================================== */
function KnowledgeTab() {
  const [kps, setKps] = useState<AdminKP[]>([]);
  const [subject, setSubject] = useState('高中数学');
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [selected, setSelected] = useState<AdminKP | null>(null);
  const [editing, setEditing] = useState<AdminKP | null>(null);
  const [showCreate, setShowCreate] = useState(false);

  const load = useCallback(async () => {
    try {
      const [listRes, graphRes] = await Promise.all([
        adminApi.listKPs({ subject }),
        adminApi.getGraph(subject),
      ]);
      setKps(listRes.knowledge_points);
      setGraph(graphRes);
    } catch { /* noop */ }
  }, [subject]);

  useEffect(() => { load(); }, [load]);

  const handleValidate = async () => {
    const res = await adminApi.validateGraph(subject);
    alert(res.message);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-lg font-semibold text-gray-800 dark:text-gray-100">知识图谱</h3>
        <div className="flex gap-2">
          <SelectSm value={subject} onChange={setSubject} options={[
            { value: '高中数学', label: '高中数学' }, { value: '高中物理', label: '高中物理' }, { value: '高中英语', label: '高中英语' },
          ]} />
          <button onClick={handleValidate} className="px-3 py-2 bg-gray-50 dark:bg-surface-600 border border-gray-200 dark:border-gray-500 rounded-lg text-xs font-medium hover:bg-gray-100 transition-colors">校验DAG</button>
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-1 px-3 py-2 bg-brand-500 text-white rounded-lg text-xs font-medium hover:bg-brand-600 transition-colors"><Plus size={14} />新增知识点</button>
        </div>
      </div>

      <div className="flex gap-6">
        {/* Node list */}
        <div className="w-64 flex-shrink-0 space-y-1 max-h-96 overflow-y-auto">
          {kps.map(kp => (
            <button key={kp.id} onClick={() => setSelected(kp)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${selected?.id === kp.id ? 'bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-surface-600'}`}>
              <div className="font-medium truncate">{kp.name}</div>
              <div className="text-xs text-gray-400 mt-0.5">{kp.chapter || kp.subject} · {DIFF_LABELS[kp.difficulty] || kp.difficulty}</div>
            </button>
          ))}
        </div>

        {/* Node detail + graph placeholder */}
        <div className="flex-1 min-w-0 border border-gray-100 dark:border-gray-600 rounded-xl p-4 min-h-64">
          {selected ? (
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-semibold text-gray-800 dark:text-gray-100">{selected.name}</h4>
                  <p className="text-xs text-gray-500 mt-1">{selected.description || '暂无描述'}</p>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => setEditing(selected)} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-surface-600 text-gray-400"><Edit3 size={14} /></button>
                  <button onClick={async () => { await adminApi.deleteKP(selected.id); setSelected(null); load(); }} className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 text-gray-400 hover:text-red-500"><Trash2 size={14} /></button>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-gray-50 dark:bg-surface-600 rounded-lg p-2"><span className="text-gray-400">难度</span><div className="font-medium text-gray-700 dark:text-gray-200">{DIFF_LABELS[selected.difficulty] || selected.difficulty}</div></div>
                <div className="bg-gray-50 dark:bg-surface-600 rounded-lg p-2"><span className="text-gray-400">重要度</span><div className="font-medium text-gray-700 dark:text-gray-200">{'★'.repeat(selected.importance)}{'☆'.repeat(Math.max(0, 10 - selected.importance))}</div></div>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">前置依赖 ({(selected.prerequisites || []).length} 个)</p>
                <div className="flex flex-wrap gap-1">
                  {(selected.prerequisites || []).map(pid => {
                    const pre = kps.find(k => k.id === pid);
                    return <span key={pid} className="px-2 py-0.5 bg-gray-100 dark:bg-surface-600 rounded text-xs text-gray-600 dark:text-gray-300">{pre?.name || pid.slice(0, 12)}</span>;
                  })}
                  {(!selected.prerequisites || selected.prerequisites.length === 0) && <span className="text-xs text-gray-400">无（根节点）</span>}
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">后置依赖 (哪些知识点依赖此节点)</p>
                <div className="flex flex-wrap gap-1">
                  {(() => {
                    const children = kps.filter(k => (k.prerequisites || []).includes(selected.id));
                    if (children.length === 0) return <span className="text-xs text-gray-400">无（叶子节点）</span>;
                    return children.map(c => <span key={c.id} className="px-2 py-0.5 bg-brand-50 dark:bg-brand-500/10 rounded text-xs text-brand-600 dark:text-brand-400">{c.name}</span>);
                  })()}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
              {graph ? `共 ${graph.nodes.length} 个节点，${graph.edges.length} 条边 — 选择左侧节点查看详情` : '加载中...'}
            </div>
          )}
        </div>
      </div>

      {editing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setEditing(null)}>
          <div className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-elevated w-full max-w-md" onClick={e => e.stopPropagation()}>
            <h3 className="font-display text-lg font-semibold mb-4">编辑知识点</h3>
            <div className="space-y-3">
              <div><label className="text-xs text-gray-500 mb-1 block">名称</label><input value={editing.name} onChange={e => setEditing({ ...editing, name: e.target.value })} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm" /></div>
              <div><label className="text-xs text-gray-500 mb-1 block">描述</label><textarea value={editing.description || ''} onChange={e => setEditing({ ...editing, description: e.target.value })} rows={2} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm" /></div>
              <div className="grid grid-cols-2 gap-3">
                <div><label className="text-xs text-gray-500 mb-1 block">难度</label>
                  <select value={editing.difficulty} onChange={e => setEditing({ ...editing, difficulty: e.target.value })} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm">
                    {['easy','medium','hard','challenge'].map(d => <option key={d} value={d}>{DIFF_LABELS[d]}</option>)}
                  </select>
                </div>
                <div><label className="text-xs text-gray-500 mb-1 block">重要度 (1-10)</label><input type="number" min={1} max={10} value={editing.importance} onChange={e => setEditing({ ...editing, importance: parseInt(e.target.value) || 5 })} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm" /></div>
              </div>
              <div><label className="text-xs text-gray-500 mb-1 block">章节</label><input value={editing.chapter || ''} onChange={e => setEditing({ ...editing, chapter: e.target.value })} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm" /></div>
            </div>
            <div className="flex justify-end gap-2 mt-5">
              <button onClick={() => setEditing(null)} className="px-4 py-2 text-sm text-gray-500 hover:bg-gray-100 dark:hover:bg-surface-600 rounded-lg">取消</button>
              <button onClick={async () => { await adminApi.updateKP(editing.id, { name: editing.name, description: editing.description, difficulty: editing.difficulty, importance: editing.importance, chapter: editing.chapter }); setEditing(null); load(); }} className="px-4 py-2 bg-brand-500 text-white text-sm rounded-lg hover:bg-brand-600">保存</button>
            </div>
          </div>
        </div>
      )}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setShowCreate(false)}>
          <CreateKPModal subject={subject} onClose={() => setShowCreate(false)} onSaved={() => { setShowCreate(false); load(); }} />
        </div>
      )}
    </div>
  );
}

function CreateKPModal({ subject, onClose, onSaved }: { subject: string; onClose: () => void; onSaved: () => void }) {
  const [name, setName] = useState('');
  const [chapter, setChapter] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [importance, setImportance] = useState(5);
  const [desc, setDesc] = useState('');
  const [saving, setSaving] = useState(false);

  const save = async () => {
    if (!name.trim()) return;
    setSaving(true);
    await adminApi.createKP({ subject, name: name.trim(), chapter: chapter.trim(), difficulty, importance, description: desc.trim() });
    setSaving(false);
    onSaved();
  };

  return (
    <div className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-elevated w-full max-w-md" onClick={e => e.stopPropagation()}>
      <h3 className="font-display text-lg font-semibold mb-4">新增知识点</h3>
      <div className="space-y-3">
        <div><label className="text-xs text-gray-500 mb-1 block">名称 *</label><input value={name} onChange={e => setName(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm" autoFocus /></div>
        <div><label className="text-xs text-gray-500 mb-1 block">章节</label><input value={chapter} onChange={e => setChapter(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm" /></div>
        <div className="grid grid-cols-2 gap-3">
          <div><label className="text-xs text-gray-500 mb-1 block">难度</label>
            <select value={difficulty} onChange={e => setDifficulty(e.target.value)} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm">
              {['easy','medium','hard','challenge'].map(d => <option key={d} value={d}>{DIFF_LABELS[d]}</option>)}
            </select>
          </div>
          <div><label className="text-xs text-gray-500 mb-1 block">重要度</label><input type="number" min={1} max={10} value={importance} onChange={e => setImportance(parseInt(e.target.value) || 5)} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm" /></div>
        </div>
        <div><label className="text-xs text-gray-500 mb-1 block">描述</label><textarea value={desc} onChange={e => setDesc(e.target.value)} rows={2} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm" /></div>
      </div>
      <div className="flex justify-end gap-2 mt-5">
        <button onClick={onClose} className="px-4 py-2 text-sm text-gray-500 hover:bg-gray-100 dark:hover:bg-surface-600 rounded-lg">取消</button>
        <button onClick={save} disabled={saving || !name.trim()} className="px-4 py-2 bg-brand-500 text-white text-sm rounded-lg hover:bg-brand-600 disabled:opacity-50">创建</button>
      </div>
    </div>
  );
}

/* ===================================================================
 * Tab: Stats
 * =================================================================== */
function StatsTab() {
  const [overview, setOverview] = useState({ total_learners: 0, active_today: 0, total_sessions: 0, total_messages: 0 });
  const [users, setUsers] = useState<Array<Record<string, unknown>>>([]);
  const [trend, setTrend] = useState<Array<{ date: string; count: number }>>([]);

  useEffect(() => {
    adminApi.getStatsOverview().then(setOverview).catch(() => {});
    adminApi.getStatsUsers({ sort_by: 'updated_at', page: 1, page_size: 20 }).then(r => setUsers(r.users)).catch(() => {});
    adminApi.getStatsDaily(30).then(r => setTrend(r.trend)).catch(() => {});
  }, []);

  const maxCount = Math.max(1, ...trend.map(t => t.count));

  return (
    <div className="space-y-6">
      <h3 className="font-display text-lg font-semibold text-gray-800 dark:text-gray-100">数据统计</h3>

      {/* Overview cards */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: '总用户', value: overview.total_learners, color: 'bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400' },
          { label: '今日活跃', value: overview.active_today, color: 'bg-green-50 dark:bg-green-500/10 text-green-600 dark:text-green-400' },
          { label: '总会话', value: overview.total_sessions, color: 'bg-accent-50 dark:bg-accent-500/10 text-accent-600 dark:text-accent-400' },
          { label: '总消息', value: overview.total_messages, color: 'bg-warning-50 dark:bg-warning-500/10 text-warning-600 dark:text-warning-400' },
        ].map(card => (
          <div key={card.label} className={`rounded-2xl p-4 ${card.color}`}>
            <div className="text-xs opacity-70">{card.label}</div>
            <div className="text-2xl font-bold mt-1">{card.value.toLocaleString()}</div>
          </div>
        ))}
      </div>

      {/* Trend sparkline */}
      <div>
        <p className="text-xs font-medium text-gray-500 mb-3">近30天消息趋势</p>
        <div className="h-32 flex items-end gap-0.5">
          {trend.map((t, i) => (
            <div key={i} className="flex-1 bg-brand-400 dark:bg-brand-500 rounded-t-sm hover:bg-brand-500 transition-colors"
              style={{ height: `${Math.max(4, (t.count / maxCount) * 100)}%` }}
              title={`${t.date}: ${t.count} 条`} />
          ))}
        </div>
      </div>

      {/* User table */}
      <div>
        <p className="text-xs font-medium text-gray-500 mb-2">用户活跃排行</p>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 dark:border-gray-600 text-left">
              <th className="pb-2 font-medium text-gray-400 w-8">#</th>
              <th className="pb-2 font-medium text-gray-400">昵称</th>
              <th className="pb-2 font-medium text-gray-400">角色</th>
              <th className="pb-2 font-medium text-gray-400">年级</th>
              <th className="pb-2 font-medium text-gray-400">会话数</th>
              <th className="pb-2 font-medium text-gray-400">消息数</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u, i) => (
              <tr key={u.id as string} className="border-b border-gray-50 dark:border-gray-700">
                <td className="py-2 text-gray-400">{i + 1}</td>
                <td className="py-2 text-gray-700 dark:text-gray-200">{u.nickname as string}</td>
                <td className="py-2 text-xs text-gray-500">{u.role as string}</td>
                <td className="py-2 text-xs text-gray-500">{(u.grade as string) || '—'}</td>
                <td className="py-2 text-xs">{u.session_count as number}</td>
                <td className="py-2 text-xs">{u.message_count as number}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ===================================================================
 * Tab: Config
 * =================================================================== */
function ConfigTab() {
  const [configs, setConfigs] = useState<Record<string, ConfigItem[]>>({});
  const [editing, setEditing] = useState<ConfigItem | null>(null);

  const load = async () => {
    const res = await adminApi.listConfig();
    setConfigs(res.configs);
  };
  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-6">
      <h3 className="font-display text-lg font-semibold text-gray-800 dark:text-gray-100">系统配置</h3>

      {Object.entries(configs).map(([cat, items]) => (
        <div key={cat}>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">{cat}</p>
          <div className="space-y-2">
            {items.map(cfg => (
              <div key={cfg.key} className="flex items-center justify-between py-2.5 px-4 bg-gray-50 dark:bg-surface-600 rounded-xl">
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-200">{cfg.key}</p>
                  <p className="text-xs text-gray-400">{cfg.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  <code className="text-xs bg-white dark:bg-surface-700 px-2 py-1 rounded font-mono text-gray-600 dark:text-gray-300 max-w-48 truncate">{cfg.value}</code>
                  <button onClick={() => setEditing(cfg)} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-surface-500 text-gray-400"><Edit3 size={13} /></button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {editing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setEditing(null)}>
          <div className="bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-elevated w-full max-w-sm" onClick={e => e.stopPropagation()}>
            <h3 className="font-display text-lg font-semibold mb-4">编辑配置</h3>
            <div className="space-y-3">
              <div><label className="text-xs text-gray-500 mb-1 block">键</label><input value={editing.key} disabled className="w-full px-3 py-2 bg-gray-100 dark:bg-surface-700 border rounded-lg text-sm text-gray-400" /></div>
              <div><label className="text-xs text-gray-500 mb-1 block">新值</label><input value={editing.value} onChange={e => setEditing({ ...editing, value: e.target.value })} className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border rounded-lg text-sm" autoFocus /></div>
              <p className="text-xs text-warning-500">⚠ 部分配置需要重启服务后生效</p>
            </div>
            <div className="flex justify-end gap-2 mt-5">
              <button onClick={() => setEditing(null)} className="px-4 py-2 text-sm text-gray-500 hover:bg-gray-100 dark:hover:bg-surface-600 rounded-lg">取消</button>
              <button onClick={async () => { await adminApi.updateConfig(editing.key, { value: editing.value }); setEditing(null); load(); }} className="px-4 py-2 bg-brand-500 text-white text-sm rounded-lg hover:bg-brand-600">保存</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ===================================================================
 * Tab: Monitor (placeholder)
 * =================================================================== */
function MonitorTab() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <Activity size={48} className="text-gray-300 dark:text-gray-600 mb-4" />
      <h3 className="font-display text-lg font-semibold text-gray-500 dark:text-gray-400 mb-2">模型效果监控</h3>
      <p className="text-sm text-gray-400 max-w-md leading-relaxed">
        该功能将在 <strong>M2 认知诊断模块</strong> 上线后启用。<br />
        届时将展示 NeuralCD 诊断准确率、试题质量分布、自适应出题效果评估。
      </p>
    </div>
  );
}

/* ===================================================================
 * Shared: small select
 * =================================================================== */
function SelectSm({ value, onChange, options }: { value: string; onChange: (v: string) => void; options: { value: string; label: string }[] }) {
  return (
    <select value={value} onChange={e => onChange(e.target.value)}
      className="px-2.5 py-2 bg-gray-50 dark:bg-surface-600 border border-gray-200 dark:border-gray-500 rounded-lg text-xs text-gray-600 dark:text-gray-300">
      {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  );
}
