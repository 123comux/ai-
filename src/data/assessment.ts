import type { AbilityReport } from '@/types/index';

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

export const mockDirections = [
  { id: '1', name: 'AI 算法工程师', description: '机器学习、深度学习、大模型微调', color: '#165dff' },
  { id: '2', name: 'AI 产品经理', description: 'AI 产品设计、Prompt Engineering', color: '#7c3aed' },
  { id: '3', name: 'AIGC 应用人才', description: 'AI 绘画、AI 写作、AI 视频', color: '#00b42a' },
  { id: '4', name: '数据分析工程师', description: 'Python 数据分析、SQL、BI', color: '#ff7d00' },
  { id: '5', name: 'AI 应用开发', description: '大模型 API、RAG、Agent', color: '#f53f3f' },
];