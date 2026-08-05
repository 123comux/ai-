import type { AbilityReport, LearningRecord, JobMatchingResult } from '@/types/index';

export const mockAbilityReport: AbilityReport = {
  overallScore: 62,
  level: '中级',
  dimensions: [
    { label: 'Python 基础', score: 75, maxScore: 100 },
    { label: '数学基础', score: 60, maxScore: 100 },
    { label: '机器学习', score: 45, maxScore: 100 },
    { label: '深度学习', score: 35, maxScore: 100 },
    { label: '大模型应用', score: 50, maxScore: 100 },
    { label: '项目经验', score: 30, maxScore: 100 },
  ],
  strengths: ['Python 语法基础扎实', '基本数据结构和算法掌握较好'],
  weaknesses: ['深度学习理论薄弱', '缺少真实项目经验', '大模型应用实践不足'],
  recommendedDirection: '大模型应用开发',
  estimatedHours: 120,
};

export const mockLearningRecords: LearningRecord[] = [
  { date: '07-28', duration: 45, lessonsCompleted: 2, exercisesDone: 8 },
  { date: '07-29', duration: 60, lessonsCompleted: 3, exercisesDone: 12 },
  { date: '07-30', duration: 30, lessonsCompleted: 1, exercisesDone: 5 },
  { date: '07-31', duration: 50, lessonsCompleted: 2, exercisesDone: 10 },
  { date: '08-01', duration: 75, lessonsCompleted: 3, exercisesDone: 15 },
  { date: '08-02', duration: 40, lessonsCompleted: 2, exercisesDone: 7 },
  { date: '08-03', duration: 55, lessonsCompleted: 2, exercisesDone: 9 },
];

export const mockJobMatchingResult: JobMatchingResult = {
  jobTitle: 'AI 应用开发实习生',
  company: '某科技公司',
  matchScore: 68,
  requiredSkills: [
    { name: 'Python', mastered: true },
    { name: '大模型 API 调用', mastered: true },
    { name: 'RAG 系统', mastered: false },
    { name: 'Agent 开发', mastered: false },
    { name: 'SQL', mastered: true },
    { name: '数据结构与算法', mastered: true },
  ],
  gapSkills: ['RAG 系统搭建', 'Agent 智能体开发', '微服务架构'],
  recommendedCourses: ['RAG 技术原理与实践', 'AI Agent 开发实战'],
  recommendedProjects: ['RAG 知识库问答系统', 'AI Agent 智能体开发'],
};