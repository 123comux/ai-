import Taro from '@tarojs/taro';

// 订阅消息模板 ID：在小程序后台「订阅消息」申请后填入对应值，留空则不请求授权。
export const SUB_TEMPLATES: Record<'checkin' | 'homework' | 'learning', string> = {
  checkin: '',   // 打卡成功提醒
  homework: '',  // 作业评审结果通知
  learning: '',  // 学习提醒/里程碑
};

/** 请求订阅消息授权。非小程序环境或模板未配置时静默跳过，不打断主流程。 */
export async function requestSubscriptions(): Promise<void> {
  if (process.env.TARO_ENV !== 'weapp') return;
  const tmplIds = Object.values(SUB_TEMPLATES).filter(Boolean);
  if (tmplIds.length === 0) return;
  try {
    const res = await Taro.requestSubscribeMessage({ tmplIds });
    console.log('[Subscribe] result:', res);
  } catch (err: any) {
    console.warn('[Subscribe] skipped:', err?.errMsg || err);
  }
}
