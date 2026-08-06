/**
 * 格式化学习时长（接收：分钟 或 秒；自动根据数值范围判断单位，输出"X小时Y分钟"或"X分钟"）
 * - 阈值 1000：< 1000 视为分钟（max 16小时≈960分钟），≥ 1000 视为秒（max 3600秒=1小时，45分钟=2700秒）
 */
export const formatDuration = (value: number): string => {
  if (!value || value < 0) return '0分钟';
  const minutes: number = value >= 1000 ? Math.round(value / 60) : value;
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  if (h === 0) return `${m}分钟`;
  if (m === 0) return `${h}小时`;
  return `${h}小时${m}分钟`;
};

/**
 * 格式化日期
 */
export const formatDate = (date: string): string => {
  const d = new Date(date);
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${month}-${day}`;
};

/**
 * 获取难度标签
 */
export const getDifficultyLabel = (level: string): string => {
  const map: Record<string, string> = {
    beginner: '入门',
    intermediate: '进阶',
    advanced: '高级',
  };
  return map[level] || level;
};

/**
 * 获取难度颜色
 */
export const getDifficultyColor = (level: string): string => {
  const map: Record<string, string> = {
    beginner: '#00b42a',
    intermediate: '#ff7d00',
    advanced: '#f53f3f',
  };
  return map[level] || '#86909c';
};

/**
 * 获取状态标签
 */
export const getStatusLabel = (status: string): string => {
  const map: Record<string, string> = {
    locked: '未解锁',
    available: '可参与',
    in_progress: '进行中',
    completed: '已完成',
    current: '学习中',
    pending: '待开始',
  };
  return map[status] || status;
};