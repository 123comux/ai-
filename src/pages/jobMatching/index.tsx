import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Input } from '@tarojs/components';
import Taro from '@tarojs/taro';
import ProgressBar from '@/components/ProgressBar';
import { fetchJobMatchingResult, analyzeJobMatching } from '@/services/api';
import type { JobMatchingResult } from '@/types/index';
import styles from './index.module.scss';

const JobMatchingPage: React.FC = () => {
  const [result, setResult] = useState<JobMatchingResult | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    // 默认加载已有结果
    const loadData = async () => {
      try {
        const data = await fetchJobMatchingResult();
        setResult(data);
      } catch (err) {
        console.error('[JobMatching] load error:', err);
      }
    };
    loadData();
  }, []);

  const handleAnalyze = async () => {
    if (!jobDescription.trim()) {
      Taro.showToast({ title: '请输入岗位描述', icon: 'none' });
      return;
    }
    setAnalyzing(true);
    try {
      const data = await analyzeJobMatching(jobDescription.trim());
      setResult(data);
    } catch (err) {
      console.error('[JobMatching] analyze error:', err);
      Taro.showToast({ title: '分析失败，请稍后重试', icon: 'none' });
    } finally {
      setAnalyzing(false);
    }
  };

  if (!result) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  return (
    <ScrollView className={styles.page} scrollY>
      <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
        <Text className={styles.navBack}>← 返回</Text>
      </View>
      {/* 输入区域 */}
      <View className={styles.inputSection}>
        <Text className={styles.inputLabel}>输入目标岗位描述</Text>
        <Input
          className={styles.inputBox}
          placeholder="如：AI大模型应用开发实习生，要求Python、RAG、LangChain、Agent开发"
          placeholderClass={styles.inputPlaceholder}
          value={jobDescription}
          onInput={(e) => setJobDescription(e.detail.value)}
          disabled={analyzing}
        />
        <View className={styles.analyzeButton} onClick={handleAnalyze}>
          <Text className={styles.analyzeButtonText}>{analyzing ? '分析中...' : 'AI 分析'}</Text>
        </View>
      </View>

      {/* 匹配结果 */}
      <View className={styles.resultSection}>
        <View className={styles.matchHeader}>
          <Text className={styles.matchTitle}>匹配结果</Text>
          <View className={styles.matchScore}>
            <Text className={styles.matchScoreValue}>{result.matchScore}</Text>
            <Text className={styles.matchScoreUnit}>%</Text>
          </View>
        </View>
        <ProgressBar percent={result.matchScore} height={12} color={result.matchScore >= 70 ? '#00b42a' : '#ff7d00'} />

        <Text className={styles.sectionTitle}>技能分析</Text>
        <View className={styles.skillList}>
          {result.requiredSkills.map((skill, index) => (
            <View key={index} className={styles.skillItem}>
              <Text className={styles.skillIcon}>{skill.mastered ? '✅' : '❌'}</Text>
              <Text className={styles.skillName}>{skill.name}</Text>
              <Text className={styles.skillStatus}>
                {skill.mastered ? '已掌握' : '待提升'}
              </Text>
            </View>
          ))}
        </View>
      </View>

      {/* 差距分析 */}
      {result.gapSkills.length > 0 && (
        <View className={styles.section}>
          <Text className={styles.sectionTitle}>待提升技能</Text>
          <View className={styles.gapList}>
            {result.gapSkills.map((skill, index) => (
              <View key={index} className={styles.gapItem}>
                <Text className={styles.gapIcon}>💪</Text>
                <Text className={styles.gapText}>{skill}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* 推荐补齐 */}
      <View className={styles.section}>
        <Text className={styles.sectionTitle}>推荐课程</Text>
        <View className={styles.recommendChips}>
          {result.recommendedCourses.map((course, index) => (
            <View key={index} className={styles.chip}>
              <Text className={styles.chipText}>📚 {course}</Text>
            </View>
          ))}
        </View>
      </View>

      <View className={styles.section}>
        <Text className={styles.sectionTitle}>推荐项目</Text>
        <View className={styles.recommendChips}>
          {result.recommendedProjects.map((project, index) => (
            <View key={index} className={styles.chip}>
              <Text className={styles.chipText}>🛠️ {project}</Text>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );
};

export default JobMatchingPage;