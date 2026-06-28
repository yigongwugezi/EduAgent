export interface StudentProfile {
  id: string;
  name: string;
  avatar?: string;
  major: string;
  grade: string;
  learningGoals: string[];
  dimensions: ProfileDimension[];
  lastActive: string;
  totalStudyHours: number;
  completedCourses: number;
}

export interface ProfileDimension {
  id: string;
  name: string;
  value: number;
  description: string;
  icon: string;
}

export interface LearningPath {
  id: string;
  title: string;
  description: string;
  progress: number;
  totalSteps: number;
  completedSteps: number;
  nodes: LearningNode[];
  currentLevel: string;
}

export interface LearningNode {
  id: string;
  title: string;
  type: 'lesson' | 'practice' | 'project' | 'assessment';
  status: 'completed' | 'in-progress' | 'locked' | 'available';
  resources: Resource[];
  position: { x: number; y: number };
  connections: string[];
}

export interface Resource {
  id: string;
  title: string;
  type: ResourceType;
  thumbnail?: string;
  duration?: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  createdAt: string;
  author: string;
  description: string;
  progress?: number;
  rating?: number;
  views?: number;
}

export type ResourceType =
  | 'document'
  | 'video'
  | 'mindmap'
  | 'quiz'
  | 'code'
  | 'animation'
  | 'project'
  | 'reading';

export interface Agent {
  id: string;
  name: string;
  role: string;
  avatar: string;
  status: 'idle' | 'working' | 'completed';
  specialty: string;
  color: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'agent';
  content: string;
  agentId?: string;
  timestamp: Date;
  attachments?: Attachment[];
}

export interface Attachment {
  id: string;
  type: 'image' | 'document' | 'video' | 'mindmap';
  title: string;
  url?: string;
  thumbnail?: string;
}

export interface GenerationTask {
  id: string;
  type: ResourceType;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  progress: number;
  agentId: string;
  title: string;
  createdAt: Date;
}

export interface LearningStats {
  weeklyHours: number[];
  subjectProgress: { name: string; progress: number }[];
  recentActivity: Activity[];
  streak: number;
  totalPoints: number;
}

export interface Activity {
  id: string;
  type: string;
  title: string;
  timestamp: Date;
  points: number;
}
