/**
 * API Service Layer
 *
 * Uses Taro.request() for cross-platform compatibility (WeChat mini-program + H5).
 * All data is fetched from the FastAPI backend (http://localhost:8000).
 */
import Taro from '@tarojs/taro';
import type { AbilityReport, LearningPath, Course, Project, LearningRecord, JobMatchingResult, Video } from '@/types/index';

const API_BASE = 'http://localhost:8000';

/** GET 辅助函数 */
async function apiGet<T>(path: string, timeoutMs: number = 15000): Promise<T> {
  const res = await Taro.request<T>({
    url: `${API_BASE}${path}`,
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
    url: `${API_BASE}${path}`,
    method: 'POST',
    header: { 'Content-Type': 'application/json' },
    data: body,
    timeout: timeoutMs,
    dataType: 'json',
  });
  if (res.statusCode !== 200) throw new Error(`HTTP ${res.statusCode}`);
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

/** 获取课程列表 */
export const fetchCourses = async (topic?: string): Promise<Course[]> => {
  const query = topic && topic !== 'all' ? `?topic=${encodeURIComponent(topic)}` : '';
  return apiGet<Course[]>(`/api/courses${query}`);
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

/** 获取项目分类 */
export const fetchProjectCategories = async () => {
  return apiGet<string[]>('/api/projects/topics');
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
    url: `${API_BASE}/api/tutor/chat`,
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