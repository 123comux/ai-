import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useLearningStore } from '@/store/useLearningStore';
import { fetchAssessmentQuestions, submitAssessment } from '@/services/api';
import type { AssessmentQuestion, AssessmentScoreResult } from '@/services/api';
import styles from './index.module.scss';

const AssessmentPage: React.FC = () => {
  const { setAbilityReport } = useLearningStore();
  const [step, setStep] = useState<'start' | 'doing' | 'result'>('start');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [result, setResult] = useState<AssessmentScoreResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleStart = async () => {
    setLoading(true);
    setError('');
    try {
      const qs = await fetchAssessmentQuestions(10);
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
      // 完成测评，提交到后端评分
      setLoading(true);
      try {
        const questionIds = questions.map((q) => q.id);
        const scoreResult = await submitAssessment(newAnswers, questionIds);
        setResult(scoreResult);

        // 同时更新 store 中的能力报告（用于首页展示）
        setAbilityReport({
          overallScore: Math.round((scoreResult.score / scoreResult.total) * 100),
          level: scoreResult.level === 'expert' ? '专家' : scoreResult.level === 'advanced' ? '高级' : scoreResult.level === 'intermediate' ? '中级' : '初级',
          dimensions: [],
          strengths: scoreResult.strengths,
          weaknesses: scoreResult.weaknesses,
          recommendedDirection: scoreResult.recommended_direction,
          estimatedHours: scoreResult.total * 10,
        });
      } catch (err) {
        setError('提交评分失败，请重试');
        console.error('[Assessment] submit failed:', err);
      } finally {
        setLoading(false);
      }
      setStep('result');
    }
  };

  const handleReassess = () => {
    setStep('start');
    setResult(null);
    setError('');
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
        {loading && <Text className={styles.loadingText}>提交中...</Text>}
      </View>
    );
  }

  if (step === 'result' && result) {
    return (
      <ScrollView className={styles.page} scrollY>
        <View className={styles.resultHeader}>
          <Text className={styles.resultTitle}>测评报告</Text>
          <View className={styles.scoreCircle}>
            <Text className={styles.scoreValue}>{result.score}/{result.total}</Text>
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
            <Text className={styles.recommendDesc}>答对 {result.score}/{result.total} 题</Text>
          </View>
        </View>

        <View className={styles.buttonGroup}>
          <View className={styles.primaryButton} onClick={handleBack}>
            <Text className={styles.primaryButtonText}>开始学习</Text>
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
          完成 10 道题目，精准定位你的 AI 能力水平，获取个性化学习推荐
        </Text>
        <View className={styles.startInfo}>
          <View className={styles.startInfoItem}>
            <Text className={styles.startInfoValue}>10</Text>
            <Text className={styles.startInfoLabel}>题目数</Text>
          </View>
          <View className={styles.startInfoDivider} />
          <View className={styles.startInfoItem}>
            <Text className={styles.startInfoValue}>10</Text>
            <Text className={styles.startInfoLabel}>分钟</Text>
          </View>
          <View className={styles.startInfoDivider} />
          <View className={styles.startInfoItem}>
            <Text className={styles.startInfoValue}>5</Text>
            <Text className={styles.startInfoLabel}>个方向</Text>
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