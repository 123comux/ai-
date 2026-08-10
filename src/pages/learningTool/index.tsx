import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Textarea } from '@tarojs/components';
import Taro, { useDidShow } from '@tarojs/taro';
import {
  fetchPromptTemplates, analyzePromptPractice, fetchAbilityHistory,
} from '@/services/api';
import type { PromptTemplate } from '@/services/api';
import styles from './index.module.scss';

const TABS = [
  { key: 'template', label: '模板库' },
  { key: 'practice', label: '实操台' },
  { key: 'growth', label: '成长' },
];
const CATS = ['学生', '职场', '编程', '求职'];

const LearningToolPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('template');
  const [cat, setCat] = useState('');
  const [templates, setTemplates] = useState<PromptTemplate[]>([]);
  const [question, setQuestion] = useState('');
  const [practice, setPractice] = useState<any>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [history, setHistory] = useState<any[]>([]);

  const loadTemplates = async () => {
    try { setTemplates(await fetchPromptTemplates(cat)); } catch (e) { console.error('[Tool] templates', e); }
  };
  const loadHistory = async () => {
    try {
      const d = await fetchAbilityHistory();
      setHistory(d.history);
    } catch (e) { console.error('[Tool] history', e); }
  };

  useEffect(() => { loadTemplates(); }, [cat]);
  useEffect(() => { loadHistory(); }, []);
  useDidShow(() => { loadHistory(); });

  const handleAnalyze = async () => {
    if (!question.trim()) { Taro.showToast({ title: '请输入你的提问', icon: 'none' }); return; }
    setAnalyzing(true);
    try {
      setPractice(await analyzePromptPractice(question.trim()));
    } catch (e) { console.error('[Tool] analyze', e); }
    finally { setAnalyzing(false); }
  };

  const handleCopy = (text: string) => {
    Taro.setClipboardData({
      data: text,
      success: () => Taro.showToast({ title: '已复制', icon: 'success' }),
    });
  };

  const maxScore = Math.max(100, ...history.map(h => h.score));

  return (
    <View className={styles.page}>
      <ScrollView scrollY style={{ height: '100%' }}>
        <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
          <Text className={styles.navBack}>← 返回</Text>
        </View>

        <View className={styles.tabs}>
          {TABS.map((t) => (
            <View key={t.key} className={`${styles.tab} ${activeTab === t.key ? styles.tabActive : ''}`} onClick={() => setActiveTab(t.key)}>
              <Text>{t.label}</Text>
            </View>
          ))}
        </View>

        {activeTab === 'template' && (
          <View className={styles.section}>
            <Text className={styles.sectionTitle}>提示词模板库（直接复制即用）</Text>
            <View className={styles.catTabs}>
              <View className={`${styles.catTab} ${cat === '' ? styles.catTabActive : ''}`} onClick={() => setCat('')}>全部</View>
              {CATS.map((c) => (
                <View key={c} className={`${styles.catTab} ${cat === c ? styles.catTabActive : ''}`} onClick={() => setCat(c)}>
                  <Text>{c}</Text>
                </View>
              ))}
            </View>
            <View className={styles.templateList}>
              {templates.map((t, i) => (
                <View key={i} className={styles.templateItem}>
                  <Text className={styles.templateTitle}>{t.category} · {t.title}</Text>
                  <Text className={styles.templateBody}>{t.template}</Text>
                  <View className={styles.copyBtn} onClick={() => handleCopy(t.template)}>复制</View>
                </View>
              ))}
            </View>
          </View>
        )}

        {activeTab === 'practice' && (
          <>
            <View className={styles.practiceBox}>
              <Text className={styles.sectionTitle}>在线 AI 实操练习台</Text>
              <Textarea
                className={styles.practiceInput}
                placeholder="输入你自己的想法/提问，AI 会帮你优化成高质量提示词并给出建议"
                value={question}
                onInput={(e) => setQuestion(e.detail.value)}
              />
              <View className={styles.practiceBtn} onClick={handleAnalyze}>
                <Text className={styles.practiceBtnText}>{analyzing ? '分析中...' : '优化我的提问'}</Text>
              </View>
            </View>

            {practice && (
              <View className={styles.resultBox}>
                <Text className={styles.resultLabel}>优化后提示词</Text>
                <Text className={styles.resultText}>{practice.improved_prompt}</Text>
                <Text className={styles.resultLabel}>优化建议</Text>
                <Text className={styles.resultText}>{practice.suggestion}</Text>
              </View>
            )}
          </>
        )}

        {activeTab === 'growth' && (
          <View className={styles.chartCard}>
            <Text className={styles.sectionTitle}>能力成长曲线（历次测评）</Text>
            {history.length === 0 ? (
              <View className={styles.empty}>还没有测评记录，去完成一次 AI 能力测评吧</View>
            ) : history.map((h) => (
              <View key={h.id} className={styles.scoreItem}>
                <Text className={styles.scoreDate}>{h.created_at}</Text>
                <Text className={styles.scoreValue}>{h.score}分</Text>
                <Text className={styles.scoreLevel}>{h.level}</Text>
                <View className={styles.scoreBar}>
                  <View className={styles.scoreFill} style={{ width: `${Math.max(4, (h.score / maxScore) * 100)}%` }} />
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
};

export default LearningToolPage;
