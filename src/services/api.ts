/**
 * API Service Layer
 *
 * Uses Taro.request() for cross-platform compatibility (WeChat mini-program + H5).
 * All data is fetched from the FastAPI backend (http://localhost:8000).
 */
import Taro from '@tarojs/taro';
import type { AbilityReport, LearningPath, Course, Project, LearningRecord, JobMatchingResult, Video } from '@/types/index';

// H5 dev mode & WeChat mini-program: both use direct backend URL.
// CORS is fully configured in backend config.py (allow_origins includes localhost:10087).
// This approach avoids Taro devServer proxy reliability issues.
// NOTE: WeChat mini-program requires HTTPS and domain whitelist — update this for production.
const API_BASE = 'http://localhost:8000';

/** 规范化 URL，避免双斜杠等问题 */
function buildUrl(path: string): string {
  const full = API_BASE + path;
  // 修正拼接后的多余双斜杠（保留协议部分的 ://）
  return full.replace(/([^:])\/{2,}/g, '$1/');
}

/** GET 辅助函数 */
async function apiGet<T>(path: string, timeoutMs: number = 15000): Promise<T> {
  const res = await Taro.request<T>({
    url: buildUrl(path),
    method: 'GET',
    timeout: timeoutMs,
    dataType: 'json',
  });
  if (res.statusCode !== 200) throw new Error(`HTTP ${res.statusCode}`);
  return res.data;
}

/** POST 辅助函数 */
async function apiPost<T>(path: string, body: Record<string, unknown>, timeoutMs: number = 30000): Promise<T> {
  const res = await Taro.request<T>({
    url: buildUrl(path),
    method: 'POST',
    header: { 'Content-Type': 'application/json' },
    data: body,
    timeout: timeoutMs,
    dataType: 'json',
  });
  if (res.statusCode !== 200) {
    // 后端 FastAPI 错误响应带 detail 字段（如"还有 n/m 个视频未看完"）
    const detail = (res.data as any)?.detail;
    const msg = typeof detail === 'string' ? detail : `HTTP ${res.statusCode}`;
    throw new Error(msg);
  }
  return res.data;
}

/** 获取能力报告 */
export const fetchAbilityReport = async (): Promise<AbilityReport> => {
  return apiGet<AbilityReport>('/api/user/ability-report');
};

/** 获取学习路径 */
export const fetchLearningPath = async (): Promise<LearningPath> => {
  const paths = await apiGet<LearningPath[]>('/api/learning-paths');
  return paths[0];
};

/** 获取所有学习路径 */
export const fetchLearningPaths = async (): Promise<LearningPath[]> => {
  return apiGet<LearningPath[]>('/api/learning-paths');
};

/** 标记学习路径节点完成，返回更新后的路径（解锁下一个节点） */
export const completeLearningPathNode = async (pathId: string, nodeId: string): Promise<LearningPath> => {
  // 不预编码：中文路径参数让 Taro/浏览器编码一次即可，预编码会导致双重编码 404
  return apiPost<LearningPath>(`/api/learning-paths/${pathId}/nodes/${nodeId}/complete`, {});
};

/** 获取课程列表 */
export const fetchCourses = async (topic?: string): Promise<Course[]> => {
  const query = topic && topic !== 'all' ? `?topic=${encodeURIComponent(topic)}` : '';
  return apiGet<Course[]>(`/api/courses${query}`);
};

/** 获取单个课程详情（含 chapters） */
export const fetchCourseDetail = async (courseId: string): Promise<any> => {
  return apiGet<any>(`/api/courses/${courseId}`);
};

/** 获取课程分类 */
export const fetchCourseCategories = async () => {
  const data = await apiGet<{ topics: string[] }>('/api/courses/topics');
  return data.topics;
};

/** 获取项目列表 */
export const fetchProjects = async (difficulty?: string): Promise<Project[]> => {
  const query = difficulty && difficulty !== 'all' ? `?difficulty=${encodeURIComponent(difficulty)}` : '';
  return apiGet<Project[]>(`/api/projects${query}`);
};

/** 推进项目一步（完成当前步骤），返回更新后的项目 */
export const advanceProject = async (projectId: string): Promise<Project> => {
  return apiPost<Project>(`/api/projects/${projectId}/advance`, {});
};

/** 获取项目分类 */
export const fetchProjectCategories = async () => {
  const data = await apiGet<{ topics: string[] }>('/api/projects/topics');
  return data.topics;
};

/** 获取学习记录 */
export const fetchLearningRecords = async (): Promise<LearningRecord[]> => {
  return apiGet<LearningRecord[]>('/api/user/learning-records');
};

/** 获取岗位对标结果 */
export const fetchJobMatchingResult = async (): Promise<JobMatchingResult> => {
  return apiGet<JobMatchingResult>('/api/user/job-matching');
};

/** 获取学习统计 */
export const fetchLearningStats = async (): Promise<{
  learningDays: number;
  totalHours: number;
  completedProjects: number;
  completedLessons: number;
}> => {
  return apiGet('/api/user/learning-stats');
};

/** 获取视频列表 */
export const fetchVideos = async (courseId?: string): Promise<Video[]> => {
  const query = courseId ? `?course_id=${courseId}` : '';
  return apiGet<Video[]>(`/api/videos${query}`);
};

/** 获取课程视频 */
export const fetchCourseVideos = async (courseId: string): Promise<Video[]> => {
  return apiGet<Video[]>(`/api/videos/course/${courseId}`);
};

/** 标记视频为已看完（持久化），minutes 为实际观看分钟数 */
export const completeVideo = async (videoId: string, minutes: number = 0): Promise<{ video_id: string; watched_count: number; minutes: number }> => {
  return apiPost<{ video_id: string; watched_count: number; minutes: number }>(`/api/videos/${videoId}/complete`, { minutes });
};

// ============ 测评系统 API ============

/** 测评题目类型 */
export interface AssessmentQuestion {
  id: string;
  question: string;
  options: string[];
  topic: string;
  difficulty: string;
}

/** 测评结果类型 */
export interface AssessmentScoreResult {
  score: number;
  total: number;
  level: string;
  strengths: string[];
  weaknesses: string[];
  recommended_direction: string;
}

/** 获取测评题目 */
export const fetchAssessmentQuestions = async (count: number = 10): Promise<AssessmentQuestion[]> => {
  return apiGet<AssessmentQuestion[]>(`/api/assessment/questions?count=${count}`);
};

/** 提交测评答案并获取评分结果（可附带自我描述，供 AI 分析融合推荐方向） */
export const submitAssessment = async (answers: number[], question_ids: string[], self_description: string = ''): Promise<AssessmentScoreResult> => {
  return apiPost<AssessmentScoreResult>('/api/assessment/submit', { answers, question_ids, self_description });
};

// ============ AI 功能 API ============

/** AI 模型类型定义 */
export interface TutorResponse {
  question: string;
  answer: string;
  model: string;
  tokens_generated: number;
}

export interface AbilityAnalysis {
  text: string;
  predicted_topic: string;
  topic_key: string;
  confidence: number;
  all_topics: Record<string, number>;
  recommendation: string;
}

export interface CourseRecommendation {
  id: string;
  title: string;
  topic: string;
  source: string;
  difficulty: string;
  score: number;
}

/** AI 导师问答（超时 120 秒，支持取消） */
export const askTutor = async (question: string): Promise<TutorResponse> => {
  const requestTask = Taro.request<TutorResponse>({
    url: buildUrl('/api/tutor/chat'),
    method: 'POST',
    header: { 'Content-Type': 'application/json' },
    data: { question },
    timeout: 120000,
    dataType: 'json',
  });
  const timeoutId = setTimeout(() => {
    requestTask.abort();
  }, 120000);
  try {
    const res = await requestTask;
    if (res.statusCode !== 200) throw new Error(`HTTP ${res.statusCode}`);
    return res.data;
  } catch (err: any) {
    if (err.errMsg === 'abort' || err.errMsg?.includes('abort')) {
      throw new Error('请求超时');
    }
    throw new Error(err?.message || err?.errMsg || 'AI 导师请求失败');
  } finally {
    clearTimeout(timeoutId);
  }
};

/** AI 能力分析 */
export const analyzeAbility = async (content: string): Promise<AbilityAnalysis> => {
  return apiPost<AbilityAnalysis>('/api/assessment/analyze', { content });
};

/** AI 课程推荐 */
export const getRecommendedCourses = async (interest: string, limit: number = 10): Promise<CourseRecommendation[]> => {
  const data = await apiGet<{ recommendations: CourseRecommendation[] }>(
    `/api/recommend/courses?interest=${encodeURIComponent(interest)}&limit=${limit}`,
  );
  return data.recommendations || [];
};

/** 获取 AI 模型状态 */
export const getAIModelsInfo = async () => {
  return apiGet<{
    models: {
      recommender?: { status?: string; total_items?: number; model_type?: string };
      assessment?: { status?: string; model_type?: string; num_labels?: number };
      tutor?: { status?: string; model_type?: string };
    };
  }>('/api/ai/models');
};

// ============ CMS 动态内容 API ============

/** Banner 类型 */
export interface BannerItem {
  id: number;
  title: string;
  description: string;
  image_url: string;
  link_url: string;
  sort_order: number;
}

/** 学习方向类型 */
export interface DirectionItem {
  id: number;
  name: string;
  description: string;
  color: string;
  topic_key: string;
  icon: string;
  sort_order: number;
}

/** 菜单项类型 */
export interface MenuItem {
  id: number;
  icon: string;
  label: string;
  path: string;
  section: string;
  sort_order: number;
}

/** 获取首页Banner */
export const fetchBanners = async (): Promise<BannerItem[]> => {
  return apiGet<BannerItem[]>('/api/content/banners');
};

/** 获取学习方向 */
export const fetchDirections = async (): Promise<DirectionItem[]> => {
  return apiGet<DirectionItem[]>('/api/content/directions');
};

/** 获取菜单项 */
export const fetchMenuItems = async (section: string = 'mine'): Promise<MenuItem[]> => {
  return apiGet<MenuItem[]>(`/api/content/menu-items?section=${section}`);
};