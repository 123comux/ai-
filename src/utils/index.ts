/**
 * 格式化视频时长（输入：秒，输出"X小时Y分钟"或"X分钟"）
 */
export const formatDuration = (value: number): string => {
  if (!value || value < 0) return '0分钟';
  const totalMinutes = Math.round(value / 60);
  const h = Math.floor(totalMinutes / 60);
  const m = Math.round(totalMinutes % 60);
  if (h === 0) return `${m}分钟`;
  if (m === 0) return `${h}小时`;
  return `${h}小时${m}分钟`;
};

/**
 * 格式化课程时长（输入：分钟，输出"X小时Y分钟"或"X分钟"）
 */
export const formatMinutes = (value: number): string => {
  if (!value || value < 0) return '0分钟';
  const totalMinutes = Math.round(value);
  const h = Math.floor(totalMinutes / 60);
  const m = Math.round(totalMinutes % 60);
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