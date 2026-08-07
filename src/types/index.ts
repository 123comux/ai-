// 用户信息
export interface UserInfo {
  id: string;
  nickname: string;
  avatar: string;
  grade: string;
  major: string;
  targetDirection: string;
}

// 能力维度
export interface AbilityDimension {
  label: string;
  score: number;
  maxScore: number;
}

// 能力报告
export interface AbilityReport {
  overallScore: number;
  level: string;
  dimensions: AbilityDimension[];
  strengths: string[];
  weaknesses: string[];
  recommendedDirection: string;
  estimatedHours: number;
}

// 课程小节
export interface Section {
  id: string;
  title: string;
  content: string;
  knowledge_points: string[];
  case: string;
}

// 课程章节
export interface Chapter {
  id: string;
  title: string;
  summary: string;
  duration_minutes: number;
  video_bv: string;
  video_page: number;
  sections: Section[];
}

// 课程
export interface Course {
  id: string;
  title: string;
  description: string;
  coverImg: string;
  duration: number;
  lessons: number;
  progress: number;
  category: string;
  isFree: boolean;
  chapters?: Chapter[];
  topic?: string;
  difficulty?: string;
  estimated_hours?: number;
  price?: number;
}

// 学习路径节点
export interface PathNode {
  id: string;
  title: string;
  type: 'course' | 'project' | 'quiz';
  status: 'locked' | 'current' | 'completed';
  progress: number;
  courseId?: string;
}

// 学习路径
export interface LearningPath {
  id: string;
  direction: string;
  title: string;
  totalWeeks: number;
  currentWeek: number;
  nodes: PathNode[];
  createdAt: string;
}

// 项目
export interface Project {
  id: string;
  title: string;
  description: string;
  coverImg: string;
  techStack: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedHours: number;
  stepCount: number;
  status: 'locked' | 'available' | 'in_progress' | 'completed';
  progress: number;
  isFree: boolean;
  price: number;
}

// 项目步骤
export interface ProjectStep {
  id: number;
  title: string;
  description: string;
  status: 'pending' | 'current' | 'completed';
}

// 学习记录
export interface LearningRecord {
  date: string;
  duration: number;
  lessonsCompleted: number;
  exercisesDone: number;
}

// 视频
export interface Video {
  id: string;
  title: string;
  subtitle?: string;
  description: string;
  /** 核心知识点/关键信息 */
  coreInfo?: string[];
  /** 叙事结构（教学流程） */
  narrative?: string;
  /** 视觉呈现 */
  visual?: string;
  /** 视频质量元数据 */
  quality?: {
    resolution: string;
    fps: number;
    audio: string;
    watermark: string;
  };
  url: string;
  coverUrl: string;
  /** 视频时长（秒） */
  duration: number;
  chapter: string;
  courseId: string;
  /** 用户是否已确认看完本视频 */
  completed?: boolean;
}

// 岗位对标结果
export interface JobMatchingResult {
  jobTitle: string;
  company: string;
  matchScore: number;
  requiredSkills: { name: string; mastered: boolean }[];
  gapSkills: string[];
  recommendedCourses: string[];
  recommendedProjects: string[];
}

