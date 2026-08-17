/**
 * API Service Layer
 *
 * Uses Taro.request() for cross-platform compatibility (WeChat mini-program + H5).
 * All data is fetched from the FastAPI backend (http://localhost:8000).
 */
import Taro from '@tarojs/taro';
import type { AbilityReport, LearningPath, Course, Project, LearningRecord, JobMatchingResult, Video, PortfolioItem, Goal, FavoriteItem, LoginResult, AuthUser, DepositConfig, DepositStatus, AccessConfig, AccessStatus } from '@/types/index';
import { API_BASE } from '@/config/env';
import { useAccessStore } from '@/store/useAccessStore';

// API 地址来自环境配置（见 src/config/env.ts）。生产构建注入 TARO_APP_API_BASE=HTTPS 域名，
// 微信小程序同时需在小程序后台配置该域名为合法 request/uploadFile 域名。

/** 读取本地登录态 token（与 useUserStore 共用同一 key） */
function authHeaders(): Record<string, string> {
  const t = Taro.getStorageSync('aishi_token');
  return t ? { Authorization: `Bearer ${t}` } : {};
}

/** 规范化 URL，避免双斜杠等问题 */
function buildUrl(path: string): string {
  const full = API_BASE + path;
  // 修正拼接后的多余双斜杠（保留协议部分的 ://）
  return full.replace(/([^:])\/{2,}/g, '$1/');
}

/**
 * 把后端返回的相对静态资源路径（如 /static/avatars/x.png、/static/covers/x.png）
 * 拼成完整 URL 供 <Image> 渲染；已是绝对 / 外部地址则原样返回。
 */
export function resolveAssetUrl(url: string | undefined | null): string {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) return url;
  if (url.startsWith('/')) return buildUrl(url);
  return url;
}

/**
 * 统一识别后端 403 access_denied（试用期已结束但未缴押金）。
 * 命中时把锁定状态写进 useAccessStore，前端全屏锁定遮罩即时接管。
 */
function maybeAccessDenied(res: { statusCode: number; data?: any }): boolean {
  if (res.statusCode !== 403) return false;
  const d = res.data?.detail;
  if (d && d.code === 'access_denied') {
    useAccessStore.getState().handleAccessDenied(d.access);
    return true;
  }
  return false;
}

/** GET 辅助函数 */
async function apiGet<T>(path: string, timeoutMs: number = 15000): Promise<T> {
  const res = await Taro.request<T>({
    url: buildUrl(path),
    method: 'GET',
    header: { ...authHeaders() },
    timeout: timeoutMs,
    dataType: 'json',
  });
  if (res.statusCode !== 200) {
    if (maybeAccessDenied(res)) throw new Error('功能已锁定，缴纳押金即可解锁');
    throw new Error(`HTTP ${res.statusCode}`);
  }
  return res.data;
}

/** POST 辅助函数 */
async function apiPost<T>(path: string, body: Record<string, unknown>, timeoutMs: number = 30000): Promise<T> {
  const res = await Taro.request<T>({
    url: buildUrl(path),
    method: 'POST',
    header: { 'Content-Type': 'application/json', ...authHeaders() },
    data: body,
    timeout: timeoutMs,
    dataType: 'json',
  });
  if (res.statusCode !== 200) {
    if (maybeAccessDenied(res)) throw new Error('功能已锁定，缴纳押金即可解锁');
    // 后端 FastAPI 错误响应带 detail 字段（如"还有 n/m 个视频未看完"）
    const detail = (res.data as any)?.detail;
    const msg = typeof detail === 'string' ? detail : `HTTP ${res.statusCode}`;
    throw new Error(msg);
  }
  return res.data;
}

/** PUT 辅助函数 */
async function apiPut<T>(path: string, body: Record<string, unknown>): Promise<T> {
  const res = await Taro.request<T>({
    url: buildUrl(path),
    method: 'PUT',
    header: { 'Content-Type': 'application/json', ...authHeaders() },
    data: body,
    timeout: 30000,
    dataType: 'json',
  });
  if (res.statusCode !== 200) {
    if (maybeAccessDenied(res)) throw new Error('功能已锁定，缴纳押金即可解锁');
    // 与 apiPost 一致：优先取后端 FastAPI 的 detail 错误信息
    const detail = (res.data as any)?.detail;
    throw new Error(typeof detail === 'string' ? detail : `HTTP ${res.statusCode}`);
  }
  return res.data;
}

/** DELETE 辅助函数 */
async function apiDelete<T>(path: string): Promise<T> {
  const res = await Taro.request<T>({
    url: buildUrl(path),
    method: 'DELETE',
    header: { ...authHeaders() },
    timeout: 15000,
    dataType: 'json',
  });
  if (res.statusCode !== 200) {
    if (maybeAccessDenied(res)) throw new Error('功能已锁定，缴纳押金即可解锁');
    throw new Error(`HTTP ${res.statusCode}`);
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
  // limit=100：课程 24 门超过后端默认 20，避免漏掉末尾课程
  const query = topic && topic !== 'all' ? `?topic=${encodeURIComponent(topic)}&limit=100` : '?limit=100';
  const list = await apiGet<Course[]>(`/api/courses${query}`);
  return (list || []).map((c) => ({ ...c, coverImg: resolveAssetUrl(c.coverImg) }));
};

/** 获取单个课程详情（含 chapters） */
export const fetchCourseDetail = async (courseId: string): Promise<Course> => {
  const c = await apiGet<Course>(`/api/courses/${courseId}`);
  return c ? { ...c, coverImg: resolveAssetUrl(c.coverImg) } : c;
};

/** 课程章节学习进度（七阶段课程按章节计进度） */
export const fetchCourseProgress = async (courseId: string): Promise<{
  course_id: string;
  total_chapters: number;
  completed_chapters: number;
  progress: number;
  completed_chapter_ids: string[];
}> => {
  return apiGet<{ course_id: string; total_chapters: number; completed_chapters: number; progress: number; completed_chapter_ids: string[] }>(
    `/api/courses/${courseId}/progress`,
  );
};

/** 标记某章节学完 */
export const completeCourseChapter = async (courseId: string, chapterId: string): Promise<{ ok: boolean }> => {
  return apiPost<{ ok: boolean }>(`/api/courses/${courseId}/chapters/${chapterId}/complete`, {});
};

/** 获取课程分类 */
export const fetchCourseCategories = async () => {
  const data = await apiGet<{ topics: string[] }>('/api/courses/topics');
  return data.topics;
};

/** 获取项目列表 */
export const fetchProjects = async (difficulty?: string): Promise<Project[]> => {
  // limit=100：避免项目数超过后端默认 20 时被截断
  const query = difficulty && difficulty !== 'all' ? `?difficulty=${encodeURIComponent(difficulty)}&limit=100` : '?limit=100';
  const list = await apiGet<Project[]>(`/api/projects${query}`);
  return (list || []).map((p) => ({ ...p, coverImg: resolveAssetUrl(p.coverImg) }));
};

/** 推进项目一步（完成当前步骤），返回更新后的项目 */
export const advanceProject = async (projectId: string): Promise<Project> => {
  const p = await apiPost<Project>(`/api/projects/${projectId}/advance`, {});
  return p ? { ...p, coverImg: resolveAssetUrl(p.coverImg) } : p;
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
  totalMinutes: number;
  completedProjects: number;
  completedLessons: number;
}> => {
  return apiGet('/api/user/learning-stats');
};

/** 获取视频列表 */
export const fetchVideos = async (courseId?: string): Promise<Video[]> => {
  const query = courseId ? `?course_id=${courseId}` : '';
  const list = await apiGet<Video[]>(`/api/videos${query}`);
  return (list || []).map((v) => ({ ...v, coverUrl: resolveAssetUrl(v.coverUrl) }));
};

/** 获取课程视频 */
export const fetchCourseVideos = async (courseId: string): Promise<Video[]> => {
  const list = await apiGet<Video[]>(`/api/videos/course/${courseId}`);
  return (list || []).map((v) => ({ ...v, coverUrl: resolveAssetUrl(v.coverUrl) }));
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
    if (res.statusCode !== 200) {
      if (maybeAccessDenied({ statusCode: res.statusCode, data: res.data as any })) {
        throw new Error('功能已锁定，缴纳押金即可解锁');
      }
      throw new Error(`HTTP ${res.statusCode}`);
    }
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
  const list = await apiGet<BannerItem[]>('/api/content/banners');
  return (list || []).map((b) => ({ ...b, image_url: resolveAssetUrl(b.image_url) }));
};

/** 获取学习方向 */
export const fetchDirections = async (): Promise<DirectionItem[]> => {
  return apiGet<DirectionItem[]>('/api/content/directions');
};

/** 获取菜单项 */
export const fetchMenuItems = async (section: string = 'mine'): Promise<MenuItem[]> => {
  return apiGet<MenuItem[]>(`/api/content/menu-items?section=${section}`);
};

/** 分析岗位描述（智谱 AI 岗位匹配） */
export const analyzeJobMatching = async (jobDescription: string): Promise<JobMatchingResult> => {
  return apiPost<JobMatchingResult>('/api/user/job-matching/analyze', { job_description: jobDescription }, 60000);
};

/** 获取作品集 */
export const fetchPortfolio = async (): Promise<PortfolioItem[]> => {
  const list = await apiGet<PortfolioItem[]>('/api/mine/portfolio');
  return (list || []).map((p) => ({ ...p, coverImg: resolveAssetUrl(p.coverImg) }));
};

/** 获取学习目标列表 */
export const fetchGoals = async (): Promise<Goal[]> => {
  return apiGet<Goal[]>('/api/mine/goals');
};

/** 新建学习目标 */
export const createGoal = async (data: { title: string; description?: string; target_date?: string }): Promise<Goal> => {
  return apiPost<Goal>('/api/mine/goals', data);
};

/** 更新学习目标（含标记完成） */
export const updateGoal = async (id: number, data: Partial<Goal>): Promise<Goal> => {
  return apiPut<Goal>(`/api/mine/goals/${id}`, data);
};

/** 删除学习目标 */
export const deleteGoal = async (id: number): Promise<{ ok: boolean }> => {
  return apiDelete<{ ok: boolean }>(`/api/mine/goals/${id}`);
};

/** 获取收藏列表 */
export const fetchFavorites = async (): Promise<FavoriteItem[]> => {
  const list = await apiGet<FavoriteItem[]>('/api/mine/favorites');
  return (list || []).map((f) => ({ ...f, cover_img: resolveAssetUrl(f.cover_img) }));
};

/** 添加收藏 */
export const addFavorite = async (itemType: 'course' | 'project', itemId: string): Promise<FavoriteItem> => {
  return apiPost<FavoriteItem>('/api/mine/favorites', { item_type: itemType, item_id: itemId });
};

/** 删除收藏 */
export const removeFavorite = async (id: number): Promise<{ ok: boolean }> => {
  return apiDelete<{ ok: boolean }>(`/api/mine/favorites/${id}`);
};

// ============ 登录 / 用户体系 API ============

/** 微信登录：用 wx.login 拿到的 code 换取登录态 token */
export const wechatLogin = async (code: string): Promise<LoginResult> => {
  const data = await apiPost<LoginResult>('/api/auth/wechat-login', { code });
  if (data?.user) data.user.avatar = resolveAssetUrl(data.user.avatar);
  return data;
};

/** 获取当前登录用户信息 */
export const fetchMe = async (): Promise<AuthUser> => {
  const user = await apiGet<AuthUser>('/api/auth/me');
  return user ? { ...user, avatar: resolveAssetUrl(user.avatar) } : user;
};

/** 更新当前用户资料（昵称/头像 + 学员自填的年级/专业/目标方向），后端为唯一数据源 */
export const updateProfile = async (profile: {
  nickname?: string;
  avatar?: string;
  grade?: string;
  major?: string;
  targetDirection?: string;
}): Promise<AuthUser> => {
  const body = {
    nickname: profile.nickname ?? '',
    avatar: profile.avatar ?? '',
    grade: profile.grade ?? '',
    major: profile.major ?? '',
    target_direction: profile.targetDirection ?? '',
  };
  const res = await apiPut<{ ok: boolean; user: AuthUser }>('/api/auth/profile', body);
  const user = res?.user;
  return user ? { ...user, avatar: resolveAssetUrl(user.avatar) } : user;
};

/** 上传头像文件（chooseAvatar 的临时路径会过期），返回可持久访问的完整 URL */
export const uploadAvatar = async (tempPath: string): Promise<string> => {
  const res = await Taro.uploadFile({
    url: buildUrl('/api/auth/avatar'),
    filePath: tempPath,
    name: 'file',
    header: { ...authHeaders() },
    timeout: 30000,
  });
  if (res.statusCode !== 200) {
    const raw = typeof res.data === 'string' ? res.data : '';
    try {
      const detail = JSON.parse(raw)?.detail;
      throw new Error(typeof detail === 'string' ? detail : `HTTP ${res.statusCode}`);
    } catch (e: any) {
      throw new Error(e?.message || `HTTP ${res.statusCode}`);
    }
  }
  const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
  // 后端返回相对路径 /static/avatars/xx.png，拼成完整 URL 供 <Image> 渲染
  return resolveAssetUrl(data.avatar_url);
};

// ============ 开发期"模拟切换用户"（后端 DEV_IMPERSONATE=true 才可用） ============

export interface DevUser {
  id: number;
  nickname: string;
  openid: string;
  created_at?: string;
}

/** 探测是否开放模拟切换用户 */
export const fetchDevConfig = async (): Promise<{ impersonate_enabled: boolean }> => {
  return apiGet<{ impersonate_enabled: boolean }>('/api/auth/dev/config');
};

/** 列出后台用户，供开发期切换 */
export const fetchDevUsers = async (): Promise<DevUser[]> => {
  const data = await apiGet<{ users: DevUser[] }>('/api/auth/dev/users');
  return data.users || [];
};

/** 以指定用户身份签发登录态（模拟切换） */
export const devImpersonate = async (userId: number): Promise<LoginResult> => {
  const data = await apiPost<LoginResult>(`/api/auth/dev/impersonate?user_id=${userId}`, {});
  if (data?.user) data.user.avatar = resolveAssetUrl(data.user.avatar);
  return data;
};

// ============ 押金式培训 API ============

/** 押金模型配置（金额、三锁规则、退费规则） */
export const fetchDepositConfig = async (): Promise<DepositConfig> => {
  return apiGet<DepositConfig>('/api/deposit/config');
};

/** 报名收押金（先收培训费） */
export const enrollDeposit = async (): Promise<any> => {
  return apiPost<any>('/api/deposit/enroll', {});
};

/** 查询押金状态、三锁进度与是否达标 */
export const fetchDepositStatus = async (): Promise<DepositStatus> => {
  return apiGet<DepositStatus>('/api/deposit/status');
};

/** 达标后全额退费 */
export const requestRefund = async (): Promise<any> => {
  return apiPost<any>('/api/deposit/refund', {});
};

/** 录入七阶段考核成绩（考核锁用） */
export const recordStageAssessment = async (stage: number, score: number): Promise<any> => {
  return apiPost<any>('/api/deposit/stage-assessment', { stage, score });
};

/** 提交实战项目（考核锁用） */
export const submitProject = async (passed: boolean): Promise<any> => {
  return apiPost<any>('/api/deposit/project-submit', { passed });
};

/** 标记作业通过（过程锁用） */
export const passHomework = async (passed: boolean): Promise<any> => {
  return apiPost<any>('/api/deposit/homework', { passed });
};

// ============ 功能使用权限 API（5 天免费试用 → 缴纳押金解锁） ============

/** 功能说明导语配置（公开，冷启动弹窗在登录确认前即可渲染；失败时前端有兜底文案） */
export const fetchAccessIntro = async (): Promise<AccessConfig> => {
  return apiGet<AccessConfig>('/api/access/intro');
};

/** 当前用户试用/解锁状态（服务端时间计算；试用中/已缴押金——解锁状态由服务端裁决） */
export const fetchAccessStatus = async (): Promise<AccessStatus> => {
  return apiGet<AccessStatus>('/api/access/status');
};

// ============ 作业提交 / 评审（过程锁完整闭环） ============

export interface HomeworkItem {
  stage: number;
  stage_name: string;
  title: string;
  requirement: string;
  rubric: string;
  course_id: string;
  submitted: boolean;
  content: string;
  ai_score: number | null;
  ai_feedback: string;
  status: 'none' | 'pending' | 'passed' | 'rejected';
  passed: boolean;
  updated_at: string;
}

/** 获取各阶段作业题目 */
export const fetchHomeworkQuestions = async (): Promise<HomeworkItem[]> => {
  const data = await apiGet<{ questions: HomeworkItem[] }>('/api/deposit/homework/questions');
  return data.questions || [];
};

/** 查询当前用户各阶段作业状态（题目 + 提交 + AI评分） */
export const fetchHomeworkStatus = async (): Promise<{ items: HomeworkItem[]; passed_count: number; total: number; all_passed: boolean }> => {
  return apiGet('/api/deposit/homework/status');
};

/** 提交某阶段作业（AI 评审 → 返回评分与反馈） */
export const submitHomework = async (stage: number, content: string): Promise<any> => {
  return apiPost<any>(`/api/deposit/homework/${stage}/submit`, { content }, 60000);
};
// ============ 平台化：打卡 / 排行榜 / 社区 ============

/** 每日打卡 */
export const doCheckin = async (note: string = ''): Promise<{ ok: boolean; checkin_date: string; streak: number }> => {
  return apiPost<any>('/api/community/checkin', { note });
};

/** 打卡状态（今日是否已打、连续天数） */
export const fetchCheckinStatus = async (): Promise<{ today_checked: boolean; streak: number; recent_dates: string[] }> => {
  return apiGet<any>('/api/community/checkin/status');
};

/** 学习排行榜 */
export const fetchLeaderboard = async (limit: number = 20): Promise<{ ranking: any[]; my_rank: number | null; my_total_minutes: number }> => {
  return apiGet<any>(`/api/community/leaderboard?limit=${limit}`);
};

/** 社区发帖 */
export const createPost = async (data: { title: string; content?: string; category?: string }): Promise<any> => {
  return apiPost<any>('/api/community/posts', data);
};

/** 帖子列表 */
export const fetchPosts = async (category: string = ''): Promise<any[]> => {
  const q = category ? `?category=${encodeURIComponent(category)}` : '';
  return apiGet<any[]>(`/api/community/posts${q}`);
};

/** 帖子详情 + 回复 */
export const fetchPostDetail = async (postId: number): Promise<{ post: any; replies: any[] }> => {
  return apiGet<any>(`/api/community/posts/${postId}`);
};

/** 回复帖子 */
export const replyPost = async (postId: number, content: string): Promise<any> => {
  return apiPost<any>(`/api/community/posts/${postId}/reply`, { content });
};

/** 点赞帖子 */
export const likePost = async (postId: number): Promise<any> => {
  return apiPost<any>(`/api/community/posts/${postId}/like`, {});
};

// ============ 提示词模板库 ============

export interface PromptTemplate {
  category: string;
  title: string;
  template: string;
}

/** 获取提示词模板（可按分类过滤） */
export const fetchPromptTemplates = async (category: string = ''): Promise<PromptTemplate[]> => {
  const q = category ? `?category=${encodeURIComponent(category)}` : '';
  return apiGet<PromptTemplate[]>(`/api/content/prompt-templates${q}`);
};

/** 获取模板分类 */
export const fetchPromptCategories = async (): Promise<{ categories: string[] }> => {
  return apiGet<any>('/api/content/prompt-templates/categories');
};

// ============ 在线 AI 实操练习台 ============

export interface PracticeResult {
  question: string;
  improved_prompt: string;
  suggestion: string;
  model: string;
  tokens_generated: number;
}

/** 提示词实操：优化用户提问并给建议 */
export const analyzePromptPractice = async (question: string): Promise<PracticeResult> => {
  return apiPost<PracticeResult>('/api/practice/analyze', { question });
};

// ============ 能力成长曲线 ============

export interface AbilityHistory {
  history: { id: number; score: number; level: string; dimensions: any[]; recommended_direction: string; created_at: string }[];
  count: number;
}

/** 测评历史 + 能力成长曲线数据 */
export const fetchAbilityHistory = async (): Promise<AbilityHistory> => {
  return apiGet<AbilityHistory>('/api/user/ability-history');
};

// ============ 分享解锁 + 组队学习 ============

/** 学习小组类型 */
export interface Team {
  id: number;
  name: string;
  code: string;
  owner_id: number;
  max_members: number;
  member_count: number;
  created_at: string;
  joined_at?: string;
}

/** 分享解锁记录 */
export interface ShareUnlockItem {
  id: number;
  share_type: string;
  share_target: string;
  unlocked_content: string;
  created_at: string;
}

/** 创建学习小组（返回含邀请码）。name/max_members 为后端 query 参数 */
export const createTeam = async (name: string, maxMembers: number = 5): Promise<Team> => {
  return apiPost<Team>(
    `/api/community/teams?name=${encodeURIComponent(name)}&max_members=${maxMembers}`,
    {},
  );
};

/** 通过邀请码加入小组。code 为后端 query 参数 */
export const joinTeam = async (code: string): Promise<{ ok: boolean; team: Team; message?: string }> => {
  return apiPost<{ ok: boolean; team: Team; message?: string }>(
    `/api/community/teams/join?code=${encodeURIComponent(code)}`,
    {},
  );
};

/** 我的小组列表 */
export const fetchMyTeams = async (): Promise<Team[]> => {
  const data = await apiGet<{ teams: Team[] }>('/api/community/teams/mine');
  return data.teams || [];
};

/** 小组详情 + 成员学习时长排行 */
export const fetchTeamDetail = async (teamId: number): Promise<{ team: Team; members: TeamMember[] }> => {
  return apiGet<{ team: Team; members: TeamMember[] }>(`/api/community/teams/${teamId}`);
};

/** 组内成员学习时长排行项 */
export interface TeamMember {
  id: number;
  nickname: string;
  avatar: string;
  total_minutes: number;
}

/** 分享后解锁进阶内容。share_type 为 'course'，share_target 为课程 id */
export const shareUnlock = async (
  shareType: string,
  shareTarget: string,
): Promise<{ ok: boolean; already_unlocked?: boolean; message?: string }> => {
  return apiPost<any>(
    `/api/community/share-unlock?share_type=${encodeURIComponent(shareType)}&share_target=${encodeURIComponent(shareTarget)}`,
    {},
  );
};

/** 查询当前用户已解锁的分享内容 */
export const fetchShareUnlocks = async (): Promise<ShareUnlockItem[]> => {
  const data = await apiGet<{ unlocked: ShareUnlockItem[]; count: number }>('/api/community/share-unlock/status');
  return data.unlocked || [];
};
