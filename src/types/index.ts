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
  description: string;
  url: string;
  coverUrl: string;
  duration: number;
  chapter: string;
  courseId: string;
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

