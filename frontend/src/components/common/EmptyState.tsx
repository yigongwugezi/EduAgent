import { Inbox, Sparkles } from 'lucide-react';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export default function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-6 text-center animate-fade-in-up">
      <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center mb-6 shadow-inner">
        {icon || <Inbox className="w-9 h-9 text-gray-300" />}
      </div>
      <h3 className="text-lg font-bold text-gray-700 mb-2">{title}</h3>
      {description && <p className="text-sm text-gray-400 max-w-sm mb-8 leading-relaxed">{description}</p>}
      {action}
    </div>
  );
}
