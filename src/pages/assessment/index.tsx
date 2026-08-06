import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import RadarChart from '@/components/RadarChart';
import { useLearningStore } from '@/store/useLearningStore';
import { fetchAbilityReport } from '@/services/api';
import styles from './index.module.scss';

const AssessmentPage: React.FC = () => {
  const { setAbilityReport } = useLearningStore();
  const [step, setStep] = useState<'start' | 'doing' | 'result'>('start');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);

  const questions = [
    { q: 'Python 中列表和元组的区别是什么？', options: ['可变 vs 不可变', '有序 vs 无序', '可重复 vs 不可重复', '没有区别'], answer: 0 },
    { q: '以下哪个是监督学习的例子？', options: ['聚类分析', '线性回归', '主成分分析', '关联规则'], answer: 1 },
    { q: 'Transformer 中自注意力机制的核心计算是什么？', options: ['卷积', '点积注意力', '循环', '池化'], answer: 1 },
    { q: '以下哪个不是激活函数？', options: ['ReLU', 'Sigmoid', 'Tanh', 'SVM'], answer: 3 },
    { q: '大模型中的"Prompt"指的是什么？', options: ['模型参数', '训练数据', '输入指令', '输出结果'], answer: 2 },
  ];

  const handleStart = () => {
    setStep('doing');
    setCurrentQuestion(0);
    setAnswers([]);
  };

  const handleAnswer = (index: number) => {
    const newAnswers = [...answers, index];
    setAnswers(newAnswers);

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // 完成测评，从后端获取结果
      fetchAbilityReport().then((report) => {
        setAbilityReport(report);
      }).catch((err) => {
        console.error('[Assessment] fetch report failed:', err);
      });
      setStep('result');
    }
  };

  const handleReassess = () => {
    setStep('start');
  };

  const handleBack = () => {
    Taro.navigateBack();
  };

  if (step === 'doing') {
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
          <Text className={styles.questionTitle}>{q.q}</Text>
          <View className={styles.options}>
            {q.options.map((opt, i) => (
              <View
                key={i}
                className={styles.option}
                onClick={() => handleAnswer(i)}
              >
                <Text className={styles.optionText}>{opt}</Text>
              </View>
            ))}
          </View>
        </View>
      </View>
    );
  }

  if (step === 'result') {
    const report = useLearningStore.getState().abilityReport || {
      overallScore: 0,
      level: '未评估',
      dimensions: [],
      strengths: [],
      weaknesses: [],
      recommendedDirection: '',
      estimatedHours: 0,
    };
    return (
      <ScrollView className={styles.page} scrollY>
        <View className={styles.resultHeader}>
          <Text className={styles.resultTitle}>测评报告</Text>
          <View className={styles.scoreCircle}>
            <Text className={styles.scoreValue}>{report.overallScore}</Text>
            <Text className={styles.scoreUnit}>分</Text>
          </View>
          <Text className={styles.levelText}>当前水平：{report.level}</Text>
        </View>

        <View className={styles.section}>
          <Text className={styles.sectionTitle}>能力雷达图</Text>
          <RadarChart dimensions={report.dimensions} size={400} />
        </View>

        <View className={styles.section}>
          <Text className={styles.sectionTitle}>优势</Text>
          {report.strengths.map((s, i) => (
            <View key={i} className={styles.tagItem}>
              <Text className={styles.tagIcon}>✅</Text>
              <Text className={styles.tagText}>{s}</Text>
            </View>
          ))}
        </View>

        <View className={styles.section}>
          <Text className={styles.sectionTitle}>薄弱点</Text>
          {report.weaknesses.map((w, i) => (
            <View key={i} className={styles.tagItem}>
              <Text className={styles.tagIcon}>💪</Text>
              <Text className={styles.tagText}>{w}</Text>
            </View>
          ))}
        </View>

        <View className={styles.section}>
          <Text className={styles.sectionTitle}>推荐方向</Text>
          <View className={styles.recommendCard}>
            <Text className={styles.recommendText}>{report.recommendedDirection}</Text>
            <Text className={styles.recommendDesc}>预计学习时长：{report.estimatedHours} 小时</Text>
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
          完成 5 道题目，精准定位你的 AI 能力水平，获取个性化学习推荐
        </Text>
        <View className={styles.startInfo}>
          <View className={styles.startInfoItem}>
            <Text className={styles.startInfoValue}>5</Text>
            <Text className={styles.startInfoLabel}>题目数</Text>
          </View>
          <View className={styles.startInfoDivider} />
          <View className={styles.startInfoItem}>
            <Text className={styles.startInfoValue}>5</Text>
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