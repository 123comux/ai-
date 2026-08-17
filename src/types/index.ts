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
  /** 项目分步实践指南 */
  steps?: { title: string; desc?: string; description?: string }[];
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

// 作品集项目
export interface PortfolioItem {
  id: string;
  title: string;
  description: string;
  coverImg: string;
  techStack: string[];
  difficulty: string;
  status: 'in_progress' | 'completed';
  completedSteps: number;
  totalSteps: number;
}

// 学习目标
export interface Goal {
  id: number;
  title: string;
  description: string;
  target_date: string;
  status: 'pending' | 'done';
  sort_order: number;
  created_at: string;
  updated_at: string;
}

// 收藏项
export interface FavoriteItem {
  id: number;
  item_type: 'course' | 'project';
  item_id: string;
  title: string;
  cover_img: string;
  detail_path: string;
  created_at: string;
}


// ============ 登录 / 用户体系 ============
export interface AuthUser {
  id: number;
  openid: string;
  nickname: string;
  avatar: string;
  // 学员自填资料（后端 users 表，已落库持久化）
  grade?: string;
  major?: string;
  targetDirection?: string;
}

export interface LoginResult {
  token: string;
  user: AuthUser;
}

// ============ 押金式培训（押金 / 三锁 / 退费） ============
export interface DepositConfig {
  amount: number;
  currency: string;
  time_lock_days: number;
  stages: number;
  pass_score: number;
  refund_working_days: number;
  locks: { time: string; process: string; assess: string };
  refund_rules: { amount: string; timing: string; failed: string; anti_fraud: string };
}

export interface DepositLock {
  passed: boolean;
  label: string;
  [k: string]: any;
}

export interface DepositStatus {
  enrolled: boolean;
  config?: DepositConfig;
  deposit?: {
    amount: number;
    currency: string;
    status: string;
    enrolled_at: string;
    deadline_at: string;
    refund_amount: number;
    refund_at: string;
  };
  status?: {
    completion_rate: number;
    watched_videos: number;
    total_videos: number;
    stage_scores: number[];
    stages_recorded: number;
    assessment_avg: number;
    deadline_at: string;
    days_left: number | null;
    time_lock: DepositLock;
    process_lock: DepositLock;
    assess_lock: DepositLock;
    refund_eligible: boolean;
  };
}

// ============ 功能使用权限（5 天免费试用 → 缴纳押金解锁） ============
export interface AccessFeature {
  icon: string;
  title: string;
  desc: string;
}

export interface AccessConfig {
  trial_days: number;
  trial_warn_seconds: number;
  deposit_amount: number;
  currency: string;
  refund_rules: { amount: string; timing: string; failed: string; anti_fraud: string };
  features: AccessFeature[];
  usage_intro: string;
}

export interface AccessStatus {
  user_id: number;
  in_trial: boolean;
  deposit_paid: boolean;
  access_granted: boolean;
  warn_expiring: boolean;
  trial_remaining_seconds: number;
  trial_end_at: string | null;
  trial_started_at: string;
  server_time: string;
  config?: AccessConfig;
}


