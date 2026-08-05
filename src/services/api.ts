/**
 * API Service Layer
 *
 * Fetches data from the FastAPI backend (http://localhost:8000).
 * Falls back to mock data when the backend is unavailable.
 */
import type { AbilityReport, LearningPath, Course, Project, LearningRecord, JobMatchingResult } from '@/types/index';
import { mockAbilityReport } from '@/data/assessment';
import { mockLearningPath, mockLearningPaths } from '@/data/learningPaths';
import { mockCourses, courseCategories } from '@/data/courses';
import { mockProjects, projectCategories } from '@/data/projects';
import { mockAbilityReport as mockReport, mockLearningRecords, mockJobMatchingResult } from '@/data/abilityReport';

const API_BASE = 'http://localhost:8000';

// 延迟模拟 API 调用
const delay = (ms: number = 300) => new Promise((resolve) => setTimeout(resolve, ms));

async function apiGet<T>(path: string, fallback: () => T | Promise<T>, extract?: string): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    // 如果后端返回的是包裹对象（如 {"topics": [...]}），提取指定字段
    if (extract && data && typeof data === 'object' && extract in data) {
      return data[extract] as T;
    }
    return data as T;
  } catch (err) {
    console.warn(`[API] ${path} failed, using mock:`, err);
    return fallback();
  }
}

/** 获取能力报告 */
export const fetchAbilityReport = async (): Promise<AbilityReport> => {
  return apiGet<AbilityReport>('/api/assessment/questions?count=10', async () => {
    await delay();
    return { ...mockAbilityReport };
  });
};

/** 获取学习路径 */
export const fetchLearningPath = async (): Promise<LearningPath> => {
  // 后端返回的是数组，取第一条
  return apiGet<LearningPath[]>('/api/learning-paths', async () => {
    await delay();
    return [{ ...mockLearningPath }];
  }).then(paths => paths[0] || { ...mockLearningPath });
};

/** 获取所有学习路径 */
export const fetchLearningPaths = async (): Promise<LearningPath[]> => {
  return apiGet<LearningPath[]>('/api/learning-paths', async () => {
    await delay();
    return [...mockLearningPaths];
  });
};

/** 获取课程列表 */
export const fetchCourses = async (topic?: string): Promise<Course[]> => {
  const query = topic && topic !== 'all' ? `?topic=${encodeURIComponent(topic)}` : '';
  return apiGet<Course[]>(`/api/courses${query}`, async () => {
    await delay();
    if (!topic || topic === 'all') return [...mockCourses];
    return mockCourses.filter((c) => c.category === topic);
  });
};

/** 获取课程分类 */
export const fetchCourseCategories = async () => {
  // 从后端课程列表提取 topics
  return apiGet<string[]>('/api/courses/topics', async () => {
    await delay(100);
    return [...courseCategories];
  }, 'topics');
};

/** 获取项目列表 */
export const fetchProjects = async (difficulty?: string): Promise<Project[]> => {
  const query = difficulty && difficulty !== 'all' ? `?difficulty=${encodeURIComponent(difficulty)}` : '';
  return apiGet<Project[]>(`/api/projects${query}`, async () => {
    await delay();
    if (!difficulty || difficulty === 'all') return [...mockProjects];
    return mockProjects.filter((p) => p.difficulty === difficulty);
  });
};

/** 获取项目分类 */
export const fetchProjectCategories = async () => {
  return apiGet<string[]>('/api/projects/topics', async () => {
    await delay(100);
    return [...projectCategories];
  });
};

/** 获取学习记录 */
export const fetchLearningRecords = async (): Promise<LearningRecord[]> => {
  // 后端暂无学习记录 API，直接用 mock
  await delay();
  return [...mockLearningRecords];
};

/** 获取岗位对标结果 */
export const fetchJobMatchingResult = async (): Promise<JobMatchingResult> => {
  // 后端暂无岗位对标 API，直接用 mock
  await delay();
  return { ...mockJobMatchingResult };
};

/** 获取学习统计 */
export const fetchLearningStats = async () => {
  // 后端暂无统计 API，直接用 mock
  await delay(100);
  return {
    learningDays: 15,
    totalHours: 48,
    completedProjects: 1,
    completedLessons: 12,
  };
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

/** POST 辅助函数 */
async function apiPost<T>(path: string, body: Record<string, unknown>, fallback: () => T | Promise<T>): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(30000),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as T;
  } catch (err) {
    console.warn(`[API] POST ${path} failed, using fallback:`, err);
    return fallback();
  }
}

/** AI 导师问答 */
export const askTutor = async (question: string): Promise<TutorResponse> => {
  return apiPost<TutorResponse>('/api/tutor/chat', { question }, async () => {
    await delay(500);
    return {
      question,
      answer: 'AI 导师模型正在加载中，请稍后再试。当前为离线回复。',
      model: 'fallback',
      tokens_generated: 0,
    };
  });
};

/** AI 能力分析 */
export const analyzeAbility = async (content: string): Promise<AbilityAnalysis> => {
  return apiPost<AbilityAnalysis>('/api/assessment/analyze', { content }, async () => {
    await delay(300);
    return {
      text: content.slice(0, 200),
      predicted_topic: '机器学习',
      topic_key: 'machine_learning',
      confidence: 0,
      all_topics: {},
      recommendation: 'AI 分析模型正在加载中，请稍后再试。',
    };
  });
};

/** AI 课程推荐 */
export const getRecommendedCourses = async (interest: string, limit: number = 10): Promise<CourseRecommendation[]> => {
  return apiGet<{ recommendations: CourseRecommendation[] }>(
    `/api/recommend/courses?interest=${encodeURIComponent(interest)}&limit=${limit}`,
    async () => {
      await delay(300);
      return { recommendations: [] };
    },
    'recommendations',
  ).then(data => data || []);
};

/** 获取 AI 模型状态 */
export const getAIModelsInfo = async () => {
  return apiGet<{
    models: {
      recommender?: { status?: string; total_items?: number; model_type?: string };
      assessment?: { status?: string; model_type?: string; num_labels?: number };
      tutor?: { status?: string; model_type?: string };
    };
  }>('/api/ai/models', async () => {
    await delay(100);
    return { models: {} };
  });
};