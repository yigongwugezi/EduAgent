import { useLocation, useNavigate } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

/* ===================================================================
 * 页面配置
 * =================================================================== */
const PAGE_META: Record<string, { label: string; parent?: string }> = {
  '/':          { label: '首页' },
  '/chat':      { label: 'AI 对话' },
  '/resources': { label: '资源库' },
  '/path':      { label: '学习路径' },
  '/profile':   { label: '学习画像' },
  '/analytics': { label: '学习分析' },
  '/timeline':  { label: '时间线', parent: '/analytics' },
};

/* ===================================================================
 * Breadcrumb 面包屑导航
 * 自动根据当前路径生成面包屑，支持二级嵌套
 * =================================================================== */
export default function Breadcrumb() {
  const { pathname } = useLocation();
  const navigate = useNavigate();

  // 只在子页面显示，首页不显示
  if (pathname === '/') return null;

  // 尝试精确匹配
  let meta = PAGE_META[pathname];
  // 回退：匹配 /resources/xxx → 取 /resources
  if (!meta) {
    const prefix = '/' + pathname.split('/')[1];
    meta = PAGE_META[prefix];
  }
  if (!meta) return null;

  const crumbs: { label: string; path?: string }[] = [{ label: '首页', path: '/' }];

  // 有父级时插入父级面包屑
  if (meta.parent) {
    const parent = PAGE_META[meta.parent];
    if (parent) crumbs.push({ label: parent.label, path: meta.parent });
  }

  crumbs.push({ label: meta.label });

  return (
    <nav className="flex items-center gap-1.5 mb-4 text-[11px] text-gray-400" aria-label="面包屑导航">
      {crumbs.map((crumb, i) => (
        <span key={i} className="flex items-center gap-1.5">
          {i > 0 && <ChevronRight className="w-3 h-3 text-gray-300" />}
          {crumb.path ? (
            <button
              onClick={() => navigate(crumb.path!)}
              className="hover:text-gray-600 transition-colors inline-flex items-center gap-1"
            >
              {i === 0 && <Home className="w-3 h-3" />}
              {crumb.label}
            </button>
          ) : (
            <span className="text-gray-600 font-medium">{crumb.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
