import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro, { useDidShow } from '@tarojs/taro';
import {
  fetchDepositStatus, fetchDepositConfig, enrollDeposit,
  requestRefund, recordStageAssessment, passHomework, submitProject,
  fetchVideos, completeVideo,
} from '@/services/api';
import { useUserStore } from '@/store/useUserStore';
import type { DepositStatus, DepositConfig } from '@/types/index';
import styles from './index.module.scss';

type Result = { type: 'ok' | 'err'; msg: string } | null;

const DepositPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<DepositStatus | null>(null);
  const [config, setConfig] = useState<DepositConfig | null>(null);
  const [result, setResult] = useState<Result>(null);
  const [busy, setBusy] = useState(false);

  const load = async () => {
    try {
      // 确保已登录（自动登录/恢复），否则后端返回 401
      if (!useUserStore.getState().isLoggedIn) {
        await useUserStore.getState().login();
      }
      const st = await fetchDepositStatus();
      setData(st);
      if (!st.enrolled && st.config) setConfig(st.config);
      else if (!st.enrolled) setConfig(await fetchDepositConfig());
    } catch (err: any) {
      console.error('[Deposit] load error:', err);
      setResult({ type: 'err', msg: err?.message || '加载失败' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);
  useDidShow(() => { load(); });

  const handleEnroll = async () => {
    setBusy(true); setResult(null);
    try {
      await enrollDeposit();
      Taro.showToast({ title: '报名成功，押金已记录', icon: 'success' });
      await load();
    } catch (err: any) {
      setResult({ type: 'err', msg: err?.message || '报名失败' });
    } finally { setBusy(false); }
  };

  const handleRefund = async () => {
    setBusy(true); setResult(null);
    try {
      const r = await requestRefund();
      setResult({ type: 'ok', msg: `退费成功，金额 ¥${r.refund_amount}（预计 15 个工作日内原路退回）` });
      await load();
    } catch (err: any) {
      setResult({ type: 'err', msg: err?.message || '退费失败' });
    } finally { setBusy(false); }
  };

  // 开发调试：一键模拟"全部三锁达标"（仅本地演示用，会自动看完所有视频 + 五阶段 90 分 + 作业通过 + 项目通过）
  const devSimulateAll = async () => {
    // 1) 把所有视频标记为看完（过程锁需要完课率 100%）
    const videos = await fetchVideos();
    for (const v of videos) {
      await completeVideo(v.id, 1);
    }
    // 2) 五阶段考核各录 90 分
    for (let s = 1; s <= 5; s++) await recordStageAssessment(s, 90);
    // 3) 作业 + 项目通过
    await passHomework(true);
    await submitProject(true);
    Taro.showToast({ title: '已模拟全部三锁达标，可申请退费', icon: 'success' });
    await load();
  };

  if (loading) {
    return <View className={styles.page}><Text className={styles.loadingText}>加载中…</Text></View>;
  }

  // ---------- 未报名：展示押金模型并引导报名 ----------
  if (!data?.enrolled) {
    const c = config || data?.config;
    return (
      <ScrollView className={styles.page} scrollY>
        <View className={styles.navBar} onClick={() => Taro.navigateBack()}><Text className={styles.navBack}>← 返回</Text></View>
        <View className={styles.hero}>
          <Text className={styles.heroLabel}>押金式培训 · 先收培训费</Text>
          <Text className={styles.heroAmount}>¥{c?.amount ?? 199}</Text>
          <Text className={styles.heroSub}>功能全部免费开放 · 达标全额退费，学会不花钱</Text>
        </View>

        <View className={styles.section}>
          <Text className={styles.sectionTitle}>三道达标门槛（三锁）</Text>
          <View className={styles.card}>
            <View className={styles.lockItem}>
              <View className={`${styles.lockIcon} ${styles.lockFailed}`}><Text>⏱</Text></View>
              <View className={styles.lockBody}>
                <Text className={styles.lockTitle}>时间锁（{c?.time_lock_days ?? 90} 天）</Text>
                <Text className={styles.lockDesc}>{c?.locks?.time}</Text>
              </View>
            </View>
            <View className={styles.lockItem}>
              <View className={`${styles.lockIcon} ${styles.lockFailed}`}><Text>✍</Text></View>
              <View className={styles.lockBody}>
                <Text className={styles.lockTitle}>过程锁</Text>
                <Text className={styles.lockDesc}>{c?.locks?.process}</Text>
              </View>
            </View>
            <View className={styles.lockItem}>
              <View className={`${styles.lockIcon} ${styles.lockFailed}`}><Text>🎓</Text></View>
              <View className={styles.lockBody}>
                <Text className={styles.lockTitle}>考核锁（均分 ≥{c?.pass_score ?? 85}）</Text>
                <Text className={styles.lockDesc}>{c?.locks?.assess}</Text>
              </View>
            </View>
          </View>
        </View>

        <View className={styles.notice}>
          退费规则：{c?.refund_rules?.amount}；{c?.refund_rules?.timing}；{c?.refund_rules?.failed}；{c?.refund_rules?.anti_fraud}。
        </View>

        {result && (
          <View className={`${styles.result} ${result.type === 'ok' ? styles.resultOk : styles.resultErr}`}>
            <Text>{result.msg}</Text>
          </View>
        )}

        <View
          className={styles.bigBtn}
          onClick={() => !busy && handleEnroll()}
        >
          <Text className={styles.bigBtnText}>{busy ? '处理中…' : `缴纳押金 ¥${c?.amount ?? 199} 并报名`}</Text>
        </View>
      </ScrollView>
    );
  }

  // ---------- 已报名：展示三锁进度 + 退费 ----------
  const st = data!.status!;
  const dep = data!.deposit!;
  const eligible = st.refund_eligible;
  const refunded = dep.status === 'refunded';

  return (
    <ScrollView className={styles.page} scrollY>
      <View className={styles.navBar} onClick={() => Taro.navigateBack()}><Text className={styles.navBack}>← 返回</Text></View>

      <View className={styles.hero}>
        <Text className={styles.heroLabel}>已缴押金（达标全额退）</Text>
        <Text className={styles.heroAmount}>¥{dep.amount}</Text>
        <Text className={styles.heroSub}>
          {refunded ? '已退费' : eligible ? '已达标，可申请退费' : '继续学习，达标即可退费'}
        </Text>
        {st.days_left != null && !refunded && (
          <View className={styles.heroDeadline}><Text>时间锁剩余 {st.days_left} 天</Text></View>
        )}
      </View>

      <View className={styles.section}>
        <Text className={styles.sectionTitle}>三锁进度</Text>
        <View className={styles.card}>
          {/* 时间锁 */}
          <View className={styles.lockItem}>
            <View className={`${styles.lockIcon} ${st.time_lock.passed ? styles.lockPassed : styles.lockFailed}`}>
              <Text>{st.time_lock.passed ? '✓' : '✗'}</Text>
            </View>
            <View className={styles.lockBody}>
              <Text className={styles.lockTitle}>时间锁（{config?.time_lock_days ?? 90} 天）</Text>
              <Text className={styles.lockDesc}>{st.time_lock.label}</Text>
            </View>
          </View>

          {/* 过程锁 */}
          <View className={styles.lockItem}>
            <View className={`${styles.lockIcon} ${st.process_lock.passed ? styles.lockPassed : styles.lockFailed}`}>
              <Text>{st.process_lock.passed ? '✓' : '✗'}</Text>
            </View>
            <View className={styles.lockBody}>
              <Text className={styles.lockTitle}>过程锁</Text>
              <Text className={styles.lockDesc}>{st.process_lock.label}</Text>
              <Text className={styles.lockMetric}>完课率 {st.completion_rate}%（已看 {st.watched_videos}/{st.total_videos} 节）</Text>
              <View className={styles.progressBar}>
                <View className={styles.progressFill} style={{ width: `${st.completion_rate}%` }} />
              </View>
            </View>
          </View>

          {/* 考核锁 */}
          <View className={styles.lockItem}>
            <View className={`${styles.lockIcon} ${st.assess_lock.passed ? styles.lockPassed : styles.lockFailed}`}>
              <Text>{st.assess_lock.passed ? '✓' : '✗'}</Text>
            </View>
            <View className={styles.lockBody}>
              <Text className={styles.lockTitle}>考核锁（均分 ≥{config?.pass_score ?? 85}）</Text>
              <Text className={styles.lockDesc}>{st.assess_lock.label}</Text>
              <Text className={styles.lockMetric}>
                已录 {st.stages_recorded} / {config?.stages ?? 5} 阶段 · 均分 {st.assessment_avg} · 项目{st.assess_lock.project_passed ? '已通过' : (st.assess_lock.project_submitted ? '待评审' : '未提交')}
              </Text>
              <View className={styles.progressBar}>
                <View className={styles.progressFill} style={{ width: `${st.assessment_avg}%` }} />
              </View>
            </View>
          </View>
        </View>
      </View>

      {result && (
        <View className={`${styles.result} ${result.type === 'ok' ? styles.resultOk : styles.resultErr}`}>
          <Text>{result.msg}</Text>
        </View>
      )}

      {!refunded && (
        <View
          className={`${styles.bigBtn} ${eligible ? '' : styles.bigBtnDisabled}`}
          onClick={() => eligible && !busy && handleRefund()}
        >
          <Text className={`${styles.bigBtnText} ${eligible ? '' : styles.bigBtnDisabledText}`}>
            {busy ? '处理中…' : eligible ? '申请全额退费' : '未达标，暂不可退'}
          </Text>
        </View>
      )}
      {refunded && (
        <View className={`${styles.bigBtn} ${styles.bigBtnDisabled}`}>
          <Text className={`${styles.bigBtnText} ${styles.bigBtnDisabledText}`}>已退费 ¥{dep.refund_amount}</Text>
        </View>
      )}

      {/* 开发调试：一键模拟全部三锁达标，便于演示退费闭环 */}
      <View className={styles.devBar}>
        <Text className={styles.devTitle}>开发调试（本地演示用）</Text>
        <View className={styles.devBtn} onClick={devSimulateAll}><Text>一键模拟：看完所有视频 + 5 阶段 90 分 + 作业 + 项目</Text></View>
      </View>
    </ScrollView>
  );
};

export default DepositPage;
