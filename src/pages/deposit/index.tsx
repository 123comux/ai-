import React, { useEffect, useRef, useState } from 'react';
import { View, Text, ScrollView, Textarea, Button } from '@tarojs/components';
import Taro, { useDidShow, useDidHide, useShareAppMessage } from '@tarojs/taro';
import {
  fetchDepositStatus, fetchDepositConfig, enrollDeposit,
  requestRefund, recordStageAssessment, passHomework, submitProject,
  fetchCourses, completeCourseChapter, fetchCourseVideos, completeVideo,
  fetchHomeworkStatus, submitHomework, type HomeworkItem,
} from '@/services/api';
import { useUserStore } from '@/store/useUserStore';
import { useAccessStore } from '@/store/useAccessStore';
import type { DepositStatus, DepositConfig } from '@/types/index';
import styles from './index.module.scss';

type Result = { type: 'ok' | 'err'; msg: string } | null;

// 微信支付 JSAPI 只能在小程序/公众号环境调起，网页端需要引导用户回小程序缴纳
const IS_WEAPP = process.env.TARO_ENV === 'weapp';

const DepositPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<DepositStatus | null>(null);
  const [config, setConfig] = useState<DepositConfig | null>(null);
  const [result, setResult] = useState<Result>(null);
  const [busy, setBusy] = useState(false);
  // 作业（过程锁）
  const [homeworkItems, setHomeworkItems] = useState<HomeworkItem[]>([]);
  const [hwExpandStage, setHwExpandStage] = useState<number | null>(null);
  const [hwInput, setHwInput] = useState('');
  const [hwBusy, setHwBusy] = useState(false);
  const [hwMsg, setHwMsg] = useState<Result>(null);

  // 一键分享作业：点分享时把最新通过作业写进 ref，openType=share 面板读取
  const shareRef = useRef({ title: '我在用 AI 学习，押金式培训达标全额退费', path: '/pages/deposit/index' });
  useShareAppMessage(() => shareRef.current);

  const handleShareHomework = (item: HomeworkItem) => {
    shareRef.current = {
      title: `我完成了「${item.stage_name}」阶段作业，AI 评审 ${item.ai_score} 分！`,
      path: '/pages/deposit/index',
    };
  };

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
      // 作业状态（独立于押金状态，未报名也显示作业题目）
      try {
        const hw = await fetchHomeworkStatus();
        setHomeworkItems(hw.items || []);
      } catch (hwErr) {
        console.warn('[Deposit] homework status error:', hwErr);
      }
    } catch (err: any) {
      console.error('[Deposit] load error:', err);
      setResult({ type: 'err', msg: err?.message || '加载失败' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 押金页是解锁通道：锁定遮罩不在本页拦截（否则用户永远点不到缴纳按钮）
    useAccessStore.getState().setOnUnlockPage(true);
    load();
    return () => useAccessStore.getState().setOnUnlockPage(false);
  }, []);
  useDidShow(() => {
    useAccessStore.getState().setOnUnlockPage(true);
    load();
  });
  useDidHide(() => useAccessStore.getState().setOnUnlockPage(false));

  const handleEnroll = async () => {
    setBusy(true); setResult(null);
    try {
      const r = await enrollDeposit();
      if (r.need_pay && r.pay_params) {
        // 网页端无法调起微信支付（JSAPI 需小程序/公众号环境）：报名已记录，引导回小程序缴纳，
        // 同一手机号登录后押金状态自动同步，缴完即解锁。
        if (!IS_WEAPP) {
          setResult({ type: 'err', msg: '网页端暂不支持在线支付：请在微信小程序内完成押金缴纳' });
          Taro.showModal({
            title: '请在微信小程序内支付',
            content: '押金缴纳需在微信小程序内完成。报名信息已记录，用同一手机号在小程序登录后继续缴纳即可，缴完自动解锁。',
            showCancel: false,
            confirmText: '我知道了',
          });
          await load();
          return;
        }
        // 真实微信支付：调起支付面板
        try {
          const payRes = await Taro.requestPayment(r.pay_params);
          const ok = String(payRes?.errMsg || '').includes('requestPayment:ok');
          if (!ok) throw new Error('支付未完成');
          setResult({ type: 'ok', msg: '支付成功，报名完成！' });
        } catch (payErr: any) {
          const msg = payErr?.message || payErr?.errMsg || '支付未完成';
          setResult({ type: 'err', msg: msg.includes('cancel') ? '已取消支付，可重新报名' : msg });
        }
        // 缴押金即解锁：支付成功后刷新权限状态，返回主界面锁定遮罩即时消失
        useAccessStore.getState().refresh();
        await load();
      } else {
        Taro.showToast({ title: '报名成功，押金已记录', icon: 'success' });
        // 占位报名（未配微信支付）同样即时解锁
        useAccessStore.getState().refresh();
        await load();
      }
    } catch (err: any) {
      setResult({ type: 'err', msg: err?.message || '报名失败' });
    } finally { setBusy(false); }
  };

  const handleRefund = async () => {
    setBusy(true); setResult(null);
    try {
      const r = await requestRefund();
      setResult({ type: 'ok', msg: r.timing_note || '退费申请已提交，等待人工复核' });
      await load();
    } catch (err: any) {
      setResult({ type: 'err', msg: err?.message || '退费失败' });
    } finally { setBusy(false); }
  };

  // 开发调试：一键模拟"全部三锁达标"（仅本地演示用，会自动学完所有章节 + 七阶段 90 分 + 作业通过 + 项目通过）
  const devSimulateAll = async () => {
    // 1) 先标记课程视频全部已看完（后端要求看完本章视频才能标记章节学完，空刷完课率已被拦）
    const courses = await fetchCourses();
    for (const c of courses) {
      try {
        const vs = await fetchCourseVideos(c.id);
        for (const v of vs) await completeVideo(v.id, 1);
      } catch {
        // 该课程暂无视频条目（纯文字章节）时跳过，章节标记本身没有视频门槛
      }
      // 2) 再标记七阶段课程全部章节学完（过程锁完课率按章节计）
      for (const ch of (c.chapters || [])) {
        await completeCourseChapter(c.id, ch.id);
      }
    }
    // 3) 七阶段考核各录 90 分
    for (let s = 1; s <= 7; s++) await recordStageAssessment(s, 90);
    // 4) 作业 + 项目通过
    await passHomework(true);
    await submitProject(true);
    Taro.showToast({ title: '已模拟全部三锁达标，可申请退费', icon: 'success' });
    await load();
  };

  // 提交某阶段作业：AI 评审 → 刷新状态
  const handleSubmitHomework = async (stage: number) => {
    const content = hwInput.trim();
    if (!content) {
      setHwMsg({ type: 'err', msg: '请先填写作业内容再提交' });
      return;
    }
    setHwBusy(true); setHwMsg(null);
    try {
      const r = await submitHomework(stage, content);
      setHwMsg({ type: 'ok', msg: `第 ${r.stage_name} 阶段作业：${r.passed ? '通过' : '未通过（可重交）'}（AI ${r.score} 分）` });
      setHwInput('');
      setHwExpandStage(null);
      const hw = await fetchHomeworkStatus();
      setHomeworkItems(hw.items || []);
      await load();
    } catch (err: any) {
      setHwMsg({ type: 'err', msg: err?.message || '作业提交失败' });
    } finally {
      setHwBusy(false);
    }
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
  const refundPending = dep.status === 'refund_pending';
  const payPending = dep.status === 'pending_payment';

  return (
    <ScrollView className={styles.page} scrollY>
      <View className={styles.navBar} onClick={() => Taro.navigateBack()}><Text className={styles.navBack}>← 返回</Text></View>

      <View className={styles.hero}>
        <Text className={styles.heroLabel}>已缴押金（达标全额退）</Text>
        <Text className={styles.heroAmount}>¥{dep.amount}</Text>
        <Text className={styles.heroSub}>
          {payPending ? '待支付 · 报名未完成' : (refunded ? '已退费' : refundPending ? '退费审核中（人工复核）' : eligible ? '已达标，可申请退费' : '继续学习，达标即可退费')}
        </Text>
        {!payPending && st.days_left != null && !refunded && !refundPending && (
          <View className={styles.heroDeadline}><Text>时间锁剩余 {st.days_left} 天</Text></View>
        )}
      </View>

      {payPending && (
        <View
          className={`${styles.bigBtn} ${busy ? styles.bigBtnDisabled : ''}`}
          onClick={() => !busy && handleEnroll()}
        >
          <Text className={styles.bigBtnText}>{busy ? '处理中…' : '去支付 ¥' + dep.amount}</Text>
        </View>
      )}

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

          {/* 每阶段作业（过程锁作业闭环） */}
          <View className={styles.hwSection}>
            <Text className={styles.hwTitle}>
              每阶段作业（AI 评审 · 全部通过才达标）
              {st.process_lock.homework_passed ? ' ✓ 已全部通过' : `（已通过 ${homeworkItems.filter(i => i.passed).length}/${homeworkItems.length}）`}
            </Text>
            {homeworkItems.length === 0 && (
              <Text className={styles.hwEmpty}>作业题目加载中…</Text>
            )}
            {homeworkItems.map((item) => (
              <View key={item.stage} className={styles.hwRow}>
                <View className={styles.hwRowHead}>
                  <Text className={styles.hwStage}>{item.stage_name}</Text>
                  <View className={styles.hwStatusWrap}>
                    <Text className={`${styles.hwStatus} ${item.passed ? styles.hwPassed : styles.hwNotPassed}`}>
                      {item.passed ? `✓ 已通过（AI ${item.ai_score} 分）` : (item.submitted ? '未通过 · 可重交' : '未提交')}
                    </Text>
                    {item.passed && (
                      <Button
                        className={styles.hwShareBtn}
                        openType="share"
                        onClick={() => handleShareHomework(item)}
                      >
                        分享作业
                      </Button>
                    )}
                  </View>
                </View>
                <Text className={styles.hwReq}>「{item.title}」{item.requirement}</Text>
                {hwExpandStage === item.stage && (
                  <View className={styles.hwForm}>
                    {item.submitted && item.ai_feedback && (
                      <Text className={styles.hwFeedback}>上次 AI 反馈：{item.ai_feedback}</Text>
                    )}
                    <Textarea
                      className={styles.hwTextarea}
                      value={hwInput}
                      onInput={(e) => setHwInput(e.detail.value)}
                      placeholder="在此填写你的作业内容（100 字以上更佳）…"
                      maxlength={4000}
                      autoHeight
                    />
                    <View
                      className={`${styles.hwSubmit} ${hwBusy ? styles.hwSubmitDisabled : ''}`}
                      onClick={() => !hwBusy && handleSubmitHomework(item.stage)}
                    >
                      <Text className={styles.hwSubmitText}>{hwBusy ? 'AI 评审中…' : '提交作业'}</Text>
                    </View>
                  </View>
                )}
                {!item.passed && (
                  <View
                    className={styles.hwGoBtn}
                    onClick={() => {
                      setHwExpandStage(hwExpandStage === item.stage ? null : item.stage);
                      setHwInput(item.submitted ? item.content : '');
                      setHwMsg(null);
                    }}
                  >
                    <Text className={styles.hwGoText}>{hwExpandStage === item.stage ? '收起' : (item.submitted ? '重新提交' : '去提交')}</Text>
                  </View>
                )}
              </View>
            ))}
            {hwMsg && (
              <View className={`${styles.result} ${hwMsg.type === 'ok' ? styles.resultOk : styles.resultErr}`}>
                <Text>{hwMsg.msg}</Text>
              </View>
            )}
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
                已录 {st.stages_recorded} / {config?.stages ?? 7} 阶段 · 均分 {st.assessment_avg} · 项目{st.assess_lock.project_passed ? '已通过' : (st.assess_lock.project_submitted ? '待评审' : '未提交')}
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

      {!refunded && !refundPending && (
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
      {refundPending && (
        <View className={`${styles.bigBtn} ${styles.bigBtnDisabled}`}>
          <Text className={`${styles.bigBtnText} ${styles.bigBtnDisabledText}`}>退费审核中 · 请等待人工复核</Text>
        </View>
      )}

      {/* 开发调试：一键模拟全部三锁达标，便于演示退费闭环 */}
      <View className={styles.devBar}>
        <Text className={styles.devTitle}>开发调试（本地演示用）</Text>
        <View className={styles.devBtn} onClick={devSimulateAll}><Text>一键模拟：看完所有视频 + 7 阶段 90 分 + 作业 + 项目</Text></View>
      </View>
    </ScrollView>
  );
};

export default DepositPage;
