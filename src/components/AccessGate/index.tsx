import { View, Text } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useAccessStore, formatTrialRemaining } from '@/store/useAccessStore';
import type { AccessConfig } from '@/types/index';
import styles from './index.module.scss';

// 兜底文案：后端导语配置拉取失败时保证弹窗仍可渲染（与 backend/config.py 默认值一致）
const FALLBACK_CONFIG: AccessConfig = {
  trial_days: 5,
  trial_warn_seconds: 86400,
  deposit_amount: 199,
  currency: 'CNY',
  refund_rules: {
    amount: '达标考核通过后押金全额原路退还',
    timing: '最终考核通过后 15 个工作日内到账',
    failed: '未达标：押金转为培训费，可续学一期',
    anti_fraud: '同一身份限退费 1 次；考核含 AI 监考 + 人工复核',
  },
  features: [
    { icon: '🧭', title: 'AI 能力测评', desc: '10 分钟定位你的 AI 水平与推荐方向，生成专属能力报告' },
    { icon: '📚', title: '七阶段课程', desc: '从大模型基础到求职备战，章节讲解 + 作业 + AI 评审' },
    { icon: '🛠️', title: '实战项目', desc: '动手完成能写进简历的 AI Agent 项目，一步步带你做' },
    { icon: '🗺️', title: '学习路径', desc: '按目标自动规划每日学习，进度一目了然' },
    { icon: '🤖', title: 'AI 导师', desc: '遇到问题随时提问，7×24 小时 AI 导师陪伴' },
    { icon: '💼', title: '求职匹配', desc: '岗位要求全面解析，帮你补齐能力短板' },
  ],
  usage_intro:
    '打开小程序 → 全部功能免费开放，无需付费即可使用 → 按学习路径完成七阶段课程与实战项目 → 达标后可申请能力认证。',
};

function goDeposit() {
  try {
    Taro.navigateTo({ url: '/pages/deposit/index' });
  } catch (e) { /* 交由下方兜底 */ }
  // H5 兜底：App 级组件里 navigateTo 偶发不生效，400ms 后 hash 未变则直接改路由
  if (typeof window !== 'undefined' && window.location) {
    setTimeout(() => {
      if (!window.location.hash.includes('pages/deposit')) {
        window.location.hash = '#/pages/deposit/index';
      }
    }, 400);
  }
}

export default function AccessGate() {
  const introVisible = useAccessStore((s) => s.introVisible);
  const locked = useAccessStore((s) => s.locked);
  const onUnlockPage = useAccessStore((s) => s.onUnlockPage);
  const status = useAccessStore((s) => s.status);
  const config = useAccessStore((s) => s.config);
  const confirmIntro = useAccessStore((s) => s.confirmIntro);

  const cfg: AccessConfig = config ?? FALLBACK_CONFIG;
  const amount = `¥${Math.round(cfg.deposit_amount)}`;

  // —— 锁定全屏遮罩：试用结束且未缴押金；押金缴纳页不拦截（解锁通道）——
  if (locked && !introVisible && !onUnlockPage) {
    return (
      <View className={styles.lockMask}>
        <View className={styles.lockCard}>
          <View className={styles.lockIcon}>🔒</View>
          <Text className={styles.lockTitle}>试用期已结束</Text>
          <Text className={styles.lockDesc}>
            为了保障学习效果，试用期结束后需缴纳押金 {amount} 才能继续使用全部功能。完成七阶段学习与考核达标后，押金将全额原路退还，请放心。
          </Text>
          <View className={styles.lockBtn} onClick={goDeposit}>去缴纳押金</View>
        </View>
      </View>
    );
  }

  // 非弹窗期：无任何遮罩
  if (!introVisible) return null;

  const warnHappening = status?.warn_expiring ?? false;
  // 状态拉取失败（未登录/网络异常）时按”试用中”处理，不阻断进入（fail-open）
  const inTrial = status?.in_trial ?? true;
  // 全部免费模式：无到期时间（trial_end_at 为空），不显示试用倒计时
  const allFree = !!status && !status.trial_end_at;

  return (
    <View className={styles.mask}>
      <View className={styles.card}>
        <View className={styles.header}>
          <Text className={styles.brand}>智学 AI</Text>
          <Text className={styles.subtitle}>功能使用说明</Text>
        </View>

        {/* 状态章：绿/琥珀/红，视觉区分试用中 / 即将到期 / 已锁定 */}
        {!locked && inTrial && !warnHappening && !allFree && (
          <View className={`${styles.statusChip} ${styles.statusOk}`}>
            <Text className={styles.statusDot}>●</Text>
            <Text>
              免费试用中{status ? ` · 剩余 ${formatTrialRemaining(status.trial_remaining_seconds)}` : ''}
            </Text>
          </View>
        )}
        {allFree && !locked && (
          <View className={`${styles.statusChip} ${styles.statusOk}`}>
            <Text className={styles.statusDot}>●</Text>
            <Text>当前全部功能免费开放</Text>
          </View>
        )}
        {warnHappening && (
          <View className={`${styles.statusChip} ${styles.statusWarn}`}>
            <Text className={styles.statusDot}>●</Text>
            <Text>即将到期 · 剩余 {formatTrialRemaining(status!.trial_remaining_seconds)}</Text>
          </View>
        )}
        {locked && (
          <View className={`${styles.statusChip} ${styles.statusLocked}`}>
            <Text className={styles.statusDot}>●</Text>
            <Text>试用期已结束 · 缴纳押金解锁</Text>
          </View>
        )}

        {/* 内容区：用普通 View（App 层不适合渲染页面级 ScrollView；内层已有 max-height 兜底） */}
        <View className={styles.body}>
          <Text className={styles.usageIntro}>{cfg.usage_intro}</Text>

          <View className={styles.sectionTitle}>主要功能介绍</View>
          <View className={styles.grid}>
            {cfg.features.map((f) => (
              <View key={f.title} className={styles.gridItem}>
                <Text className={styles.gridIcon}>{f.icon}</Text>
                <Text className={styles.gridTitle}>{f.title}</Text>
                <Text className={styles.gridDesc}>{f.desc}</Text>
              </View>
            ))}
          </View>

          <View className={styles.sectionTitle}>押金与退还政策</View>
          <View className={styles.policyCard}>
            <View className={styles.policyRow}><Text className={styles.policyLabel}>💰 押金金额</Text><Text className={styles.policyText}>{amount} / 一次缴纳</Text></View>
            <View className={styles.policyRow}><Text className={styles.policyLabel}>✅ 达标退还</Text><Text className={styles.policyText}>{cfg.refund_rules.amount}，{cfg.refund_rules.timing}</Text></View>
            <View className={styles.policyRow}><Text className={styles.policyLabel}>🎯 未达标</Text><Text className={styles.policyText}>{cfg.refund_rules.failed}</Text></View>
            <View className={styles.policyRow}><Text className={styles.policyLabel}>🛡️ 诚信保障</Text><Text className={styles.policyText}>{cfg.refund_rules.anti_fraud}</Text></View>
          </View>
        </View>

        <View className={styles.footer}>
          {locked ? (
            <View className={styles.primaryBtn} onClick={() => { confirmIntro(); goDeposit(); }}>
              缴纳押金，立即解锁
            </View>
          ) : (
            <View className={styles.primaryBtn} onClick={confirmIntro}>我已了解，开始使用</View>
          )}
          {locked && (
            <View className={styles.secondaryBtn} onClick={confirmIntro}>我已经了解，下次再说</View>
          )}
        </View>
      </View>
    </View>
  );
}