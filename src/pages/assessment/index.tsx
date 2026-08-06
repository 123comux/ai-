import React, { useState } from 'react';
import { View, Text, ScrollView, Input } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useLearningStore } from '@/store/useLearningStore';
import { fetchAssessmentQuestions, submitAssessment } from '@/services/api';
import type { AssessmentQuestion, AssessmentScoreResult } from '@/services/api';
import styles from './index.module.scss';

const AssessmentPage: React.FC = () => {
  const { setAbilityReport } = useLearningStore();
  const [step, setStep] = useState<'start' | 'doing' | 'describe' | 'result'>('start');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [selfDescription, setSelfDescription] = useState('');
  const [result, setResult] = useState<AssessmentScoreResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleStart = async () => {
    setLoading(true);
    setError('');
    try {
      const qs = await fetchAssessmentQuestions(20);
      if (qs.length === 0) {
        setError('暂无可用题目，请稍后再试');
        return;
      }
      setQuestions(qs);
      setStep('doing');
      setCurrentQuestion(0);
      setAnswers([]);
    } catch (err) {
      setError('加载题目失败，请检查网络连接');
      console.error('[Assessment] load questions failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (index: number) => {
    const newAnswers = [...answers, index];
    setAnswers(newAnswers);

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // 全部答完，进入自我描述步骤（可选，用于 AI 分析融合）
      setStep('describe');
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      const questionIds = questions.map((q) => q.id);
      const scoreResult = await submitAssessment(answers, questionIds, selfDescription.trim());
      setResult(scoreResult);

      // 更新 store 中的能力报告（用于首页/我的页展示）
      setAbilityReport({
        overallScore: scoreResult.score,
        level: scoreResult.level === 'expert' ? '专家' : scoreResult.level === 'advanced' ? '高级' : scoreResult.level === 'intermediate' ? '中级' : '初级',
        dimensions: [],
        strengths: scoreResult.strengths,
        weaknesses: scoreResult.weaknesses,
        recommendedDirection: scoreResult.recommended_direction,
        estimatedHours: scoreResult.total * 10,
      });
      setStep('result');
    } catch (err) {
      setError('提交评分失败，请重试');
      console.error('[Assessment] submit failed:', err);
      setStep('describe');
    } finally {
      setLoading(false);
    }
  };

  const handleReassess = () => {
    setStep('start');
    setResult(null);
    setError('');
    setSelfDescription('');
  };

  const handleBack = () => {
    Taro.navigateBack();
  };

  const getLevelLabel = (level: string) => {
    const map: Record<string, string> = {
      expert: '专家',
      advanced: '高级',
      intermediate: '中级',
      beginner: '初级',
    };
    return map[level] || level;
  };

  // 加载中
  if (loading && step === 'start') {
    return (
      <View className={styles.page}>
        <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
          <Text className={styles.navBack}>← 返回</Text>
        </View>
        <View className={styles.startContent}>
          <Text className={styles.loadingText}>加载中...</Text>
        </View>
      </View>
    );
  }

  if (error && step === 'start') {
    return (
      <View className={styles.page}>
        <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
          <Text className={styles.navBack}>← 返回</Text>
        </View>
        <View className={styles.startContent}>
          <Text className={styles.errorText}>{error}</Text>
          <View className={styles.startButton} onClick={handleStart}>
            <Text className={styles.startButtonText}>重试</Text>
          </View>
        </View>
      </View>
    );
  }

  if (step === 'doing' && questions.length > 0) {
    const q = questions[currentQuestion];
    return (
      <View className={styles.page}>
        <View className={styles.progressBar}>
          <View
            className={styles.progressFill}
            style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
          />
        </View>
        <Text className={styles.progressText}>
          {currentQuestion + 1} / {questions.length}
        </Text>
        <View className={styles.questionCard}>
          <Text className={styles.questionTitle}>{q.question}</Text>
          <View className={styles.options}>
            {q.options.map((opt, i) => (
              <View
                key={i}
                className={styles.option}
                onClick={() => !loading && handleAnswer(i)}
              >
                <Text className={styles.optionText}>{opt}</Text>
              </View>
            ))}
          </View>
        </View>
      </View>
    );
  }

  if (step === 'describe') {
    return (
      <View className={styles.page}>
        <View className={styles.navBar}>
          <Text className={styles.navBack} onClick={() => setStep('doing')}>← 上一题</Text>
        </View>
        <View className={styles.startContent}>
          <Text className={styles.startIcon}>✨</Text>
          <Text className={styles.startTitle}>介绍一下你自己</Text>
          <Text className={styles.startDesc}>
            可选。简单描述你的背景或学习目标（如「我熟悉 Python，想学大模型开发」），
            AI 会结合答题结果给出更精准的方向推荐。
          </Text>
          <View className={styles.describeBox}>
            <Input
              className={styles.describeInput}
              placeholder="例如：我是计算机专业学生，Python 基础较好，想做 AI 应用开发"
              value={selfDescription}
              onInput={(e) => setSelfDescription(e.detail.value)}
            />
          </View>
          {error && <Text className={styles.errorInline}>{error}</Text>}
          <View className={styles.buttonGroup} style={{ marginTop: '40rpx' }}>
            <View className={styles.startButton} onClick={() => !loading && handleSubmit()}>
              <Text className={styles.startButtonText}>
                {loading ? '分析中...' : '生成测评报告'}
              </Text>
            </View>
            <View className={styles.secondaryButton} onClick={() => !loading && handleSubmit()}>
              <Text className={styles.secondaryButtonText}>跳过，直接生成</Text>
            </View>
          </View>
        </View>
      </View>
    );
  }

  if (step === 'result' && result) {
    return (
      <ScrollView className={styles.page} scrollY>
        <View className={styles.resultHeader}>
          <Text className={styles.resultTitle}>测评报告</Text>
          <View className={styles.scoreCircle}>
            <Text className={styles.scoreValue}>{result.score}</Text>
            <Text className={styles.scoreUnit}>分</Text>
          </View>
          <Text className={styles.levelText}>当前水平：{getLevelLabel(result.level)}</Text>
        </View>

        <View className={styles.section}>
          <Text className={styles.sectionTitle}>优势领域</Text>
          {result.strengths.length > 0 ? result.strengths.map((s, i) => (
            <View key={i} className={styles.tagItem}>
              <Text className={styles.tagIcon}>✅</Text>
              <Text className={styles.tagText}>{s}</Text>
            </View>
          )) : <Text className={styles.emptyText}>暂无显著优势</Text>}
        </View>

        <View className={styles.section}>
          <Text className={styles.sectionTitle}>待提升领域</Text>
          {result.weaknesses.length > 0 ? result.weaknesses.map((w, i) => (
            <View key={i} className={styles.tagItem}>
              <Text className={styles.tagIcon}>💪</Text>
              <Text className={styles.tagText}>{w}</Text>
            </View>
          )) : <Text className={styles.emptyText}>暂无薄弱环节</Text>}
        </View>

        <View className={styles.section}>
          <Text className={styles.sectionTitle}>推荐方向</Text>
          <View className={styles.recommendCard}>
            <Text className={styles.recommendText}>{result.recommended_direction}</Text>
            <Text className={styles.recommendDesc}>综合答题表现生成</Text>
          </View>
        </View>

        <View className={styles.buttonGroup}>
          <View className={styles.primaryButton} onClick={() => Taro.navigateTo({ url: '/pages/learningPath/index' })}>
            <Text className={styles.primaryButtonText}>查看学习路径</Text>
          </View>
          <View className={styles.secondaryButton} onClick={handleReassess}>
            <Text className={styles.secondaryButtonText}>重新测评</Text>
          </View>
        </View>
      </ScrollView>
    );
  }

  return (
    <View className={styles.page}>
      <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
        <Text className={styles.navBack}>← 返回</Text>
      </View>
      <View className={styles.startContent}>
        <Text className={styles.startIcon}>🧠</Text>
        <Text className={styles.startTitle}>AI 能力测评</Text>
        <Text className={styles.startDesc}>
          完成 20 道题目，覆盖编程、数学、机器学习、深度学习、大模型、项目经验六大维度，
          精准定位你的 AI 能力水平
        </Text>
        <View className={styles.startInfo}>
          <View className={styles.startInfoItem}>
            <Text className={styles.startInfoValue}>20</Text>
            <Text className={styles.startInfoLabel}>题目数</Text>
          </View>
          <View className={styles.startInfoDivider} />
          <View className={styles.startInfoItem}>
            <Text className={styles.startInfoValue}>10</Text>
            <Text className={styles.startInfoLabel}>分钟</Text>
          </View>
          <View className={styles.startInfoDivider} />
          <View className={styles.startInfoItem}>
            <Text className={styles.startInfoValue}>6</Text>
            <Text className={styles.startInfoLabel}>个维度</Text>
          </View>
        </View>
        <View className={styles.startButton} onClick={handleStart}>
          <Text className={styles.startButtonText}>开始测评</Text>
        </View>
      </View>
    </View>
  );
};

export default AssessmentPage;
