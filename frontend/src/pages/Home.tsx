import { useNavigate } from 'react-router-dom';
import { useProfileStore } from '../store/profileStore';
import { useChatStore } from '../store/chatStore';
import { useLearningPath } from '../hooks/useLearningPath';
import { useResources } from '../hooks/useResources';
import { formatDuration, timeAgo } from '../utils/format';
import { RESOURCE_TYPE_LABELS } from '../utils/constants';

export default function Home() {
  const navigate = useNavigate();
  const profile = useProfileStore((s) => s.profile);
  const messages = useChatStore((s) => s.messages);
  const store = useChatStore();
  const { path } = useLearningPath();
  const { resources } = useResources();

  const hasData = messages.length > 0;
  const completeness = profile ? Math.round((profile.dimensions.length / 10) * 100) : 0;
  const currentStage = path?.stages?.find((s) =>
    s.nodes.some((n) => n.status === 'in_progress' || n.status === 'available')
  );
  const recommended = resources?.slice(0, 3) || [];

  if (!hasData) {
    return (
      <div className="flex items-center justify-center min-h-[70vh] px-6">
        <div className="text-center max-w-sm">
          <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-5">
            <span className="text-2xl">&#127919;</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">开始你的学习之旅</h2>
          <p className="text-sm text-gray-400 mb-6 leading-relaxed">
            去 AI 对话页描述你的专业、基础和目标，系统会自动为你生成个性化学习方案。
          </p>
          <button onClick={() => navigate('/chat')} className="px-5 py-2.5 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors">开始对话</button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-xl font-semibold text-gray-900">
          {store.messages.filter(m => m.role === 'user').length} 轮对话 &middot; {completeness}% 画像完整
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          {profile?.dimensions?.find(d => d.key === 'knowledge_base')?.description || '继续完善你的学习画像'}
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        <button onClick={() => navigate('/path')} className="bg-white border border-gray-200 rounded-lg p-4 text-left hover:border-gray-300 transition-colors">
          <p className="text-xs text-gray-400 mb-1">当前课程</p>
          <p className="text-sm font-medium text-gray-800 truncate">{path?.courseName || profile?.dimensions?.find(d => d.key === 'knowledge_base')?.description || '&mdash;'}</p>
          {path && <p className="text-xs text-gray-400 mt-2">{path.overallProgress}% &middot; {path.estimatedDays} 天</p>}
        </button>

        <button onClick={() => navigate('/profile')} className="bg-white border border-gray-200 rounded-lg p-4 text-left hover:border-gray-300 transition-colors">
          <p className="text-xs text-gray-400 mb-1">画像完整度</p>
          <p className="text-sm font-medium text-gray-800">{completeness}%</p>
          <div className="h-1.5 bg-gray-100 rounded-full mt-2 overflow-hidden">
            <div className={'h-full rounded-full transition-all ' + (completeness >= 80 ? 'bg-green-500' : completeness >= 50 ? 'bg-amber-500' : 'bg-red-400')} style={{ width: completeness + '%' }} />
          </div>
        </button>

        <button onClick={() => navigate('/path')} className="bg-white border border-gray-200 rounded-lg p-4 text-left hover:border-gray-300 transition-colors">
          <p className="text-xs text-gray-400 mb-1">学习阶段</p>
          <p className="text-sm font-medium text-gray-800 truncate">{currentStage?.title || '&mdash;'}</p>
          {currentStage && <p className="text-xs text-gray-400 mt-2">{currentStage.estimatedDays} 天</p>}
        </button>

        <button onClick={() => navigate('/chat')} className="bg-gray-900 text-white rounded-lg p-4 text-left hover:bg-gray-800 transition-colors">
          <p className="text-xs text-gray-400 mb-1">继续学习</p>
          <p className="text-sm font-medium">进入对话 &rarr;</p>
          <p className="text-xs text-gray-400 mt-2">{timeAgo(messages[messages.length - 1]?.timestamp || Date.now())}</p>
        </button>
      </div>

      {recommended.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-700 mb-3">推荐资源</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {recommended.map((r) => (
              <button key={r.id} onClick={() => navigate('/resources')} className="bg-white border border-gray-200 rounded-lg p-4 text-left hover:border-gray-300 transition-colors">
                <p className="text-sm font-medium text-gray-800 truncate">{r.title}</p>
                <p className="text-xs text-gray-400 mt-1">{RESOURCE_TYPE_LABELS[r.type] || r.type} &middot; {formatDuration(r.estimatedMinutes)}</p>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
