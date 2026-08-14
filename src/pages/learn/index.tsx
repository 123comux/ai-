import React, { useCallback, useEffect, useRef, useState } from 'react';
import { View, Text, ScrollView, Input } from '@tarojs/components';
import Taro, { useDidShow } from '@tarojs/taro';
import CourseCard from '@/components/CourseCard';
import PathCard from '@/components/PathCard';
import { useLearningStore } from '@/store/useLearningStore';
import { fetchCourses, fetchLearningPath, fetchCourseCategories, getRecommendedCourses } from '@/services/api';
import type { Course } from '@/types/index';
import type { CourseRecommendation } from '@/services/api';
import styles from './index.module.scss';

/** 课程 topic/stage 中文映射 */
const TOPIC_LABEL_MAP: Record<string, string> = {
  '大模型基础': '阶段一 · 大模型基础',
  'Agent基础': '阶段二 · Agent 概念',
  '开发实战': '阶段三 · 开发实战',
  '多Agent': '阶段四 · 多 Agent',
  '优化部署': '阶段五 · 优化部署',
  '项目实战': '阶段六 · 项目实战',
  '求职备战': '阶段七 · 求职备战',
  'all': '全部',
  'beginner': '入门',
  'intermediate': '进阶',
  'advanced': '高级',
};

const LearnPage: React.FC = () => {
  const { currentPath, setCurrentPath } = useLearningStore();
  const [courses, setCourses] = useState<Course[]>([]);
  const [categories, setCategories] = useState<{ key: string; label: string }[]>([]);
  const [activeCategory, setActiveCategory] = useState('all');

  // AI 课程推荐
  const [recommendInterest, setRecommendInterest] = useState('');
  const [recommendResults, setRecommendResults] = useState<CourseRecommendation[]>([]);
  const [recommendLoading, setRecommendLoading] = useState(false);
  const [showRecommend, setShowRecommend] = useState(false);

  const firstShow = useRef(true);

  const loadData = useCallback(async () => {
    try {
      // 读取从首页传递的学习方向
      const topic = useLearningStore.getState().selectedTopic;
      const loadTopic = topic !== 'all' ? topic : undefined;

      const [courseData, catData, pathData] = await Promise.all([
        fetchCourses(loadTopic),
        fetchCourseCategories(),
        fetchLearningPath(),
      ]);
      setCourses(courseData);
      setCategories(catData.map((c: string) => ({ key: c, label: TOPIC_LABEL_MAP[c] || c })));
      if (topic !== 'all' && catData.includes(topic)) {
        setActiveCategory(topic);
      }
      setCurrentPath(pathData);
    } catch (err) {
      console.error('[Learn] load data error:', err);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Tab 页切回时重新拉取，避免看到旧数据
  useDidShow(() => {
    if (firstShow.current) { firstShow.current = false; return; }
    loadData();
  });

  const handleCategoryChange = async (key: string) => {
    setActiveCategory(key);
    try {
      const data = await fetchCourses(key);
      setCourses(data);
    } catch (err) {
      console.error('[Learn] filter error:', err);
    }
  };

  const handleViewCourse = (id: string) => {
    Taro.navigateTo({ url: `/pages/courseDetail/index?id=${id}` });
  };

  const handleViewPath = () => {
    Taro.navigateTo({ url: '/pages/learningPath/index' });
  };

  const handleRecommend = async () => {
    const interest = recommendInterest.trim();
    if (!interest || recommendLoading) return;
    setRecommendLoading(true);
    setShowRecommend(true);
    try {
      const res = await getRecommendedCourses(interest, 8);
      setRecommendResults(res);
    } catch {
      setRecommendResults([]);
    } finally {
      setRecommendLoading(false);
    }
  };

  const handleBackHome = () => {
    Taro.switchTab({ url: '/pages/home/index' });
  };

  return (
    <ScrollView className={styles.page} scrollY>
      {/* 返回首页 */}
      <View className={styles.backHome} onClick={handleBackHome}>
        <Text className={styles.backHomeText}>← 返回首页</Text>
      </View>
      {/* AI 课程推荐搜索 */}
      <View className={styles.section}>
        <View className={styles.sectionHeader}>
          <Text className={styles.sectionTitle}>AI 课程推荐</Text>
        </View>
        <View className={styles.recommendBar}>
          <Input
            className={styles.recommendInput}
            placeholder="输入你感兴趣的方向，如：机器学习、Python..."
            value={recommendInterest}
            onInput={(e) => setRecommendInterest(e.detail.value)}
            onConfirm={handleRecommend}
            disabled={recommendLoading}
            confirmType="search"
          />
          <View className={styles.recommendBtn} onClick={handleRecommend}>
            <Text className={styles.recommendBtnText}>推荐</Text>
          </View>
        </View>
        {showRecommend && (
          <View className={styles.recommendResults}>
            {recommendLoading ? (
              <Text className={styles.recommendLoading}>正在为你智能推荐...</Text>
            ) : recommendResults.length > 0 ? (
              <View className={styles.recommendList}>
                {recommendResults.map((item, i) => (
                  <View key={i} className={styles.recommendItem} onClick={() => handleViewCourse(item.id)}>
                    <Text className={styles.recommendItemTitle}>{item.title}</Text>
                    <Text className={styles.recommendItemMeta}>
                      {TOPIC_LABEL_MAP[item.topic] || item.topic} · {TOPIC_LABEL_MAP[item.difficulty] || item.difficulty} · 匹配度 {Math.round(item.score * 100)}%
                    </Text>
                  </View>
                ))}
              </View>
            ) : (
              <Text className={styles.recommendEmpty}>暂无推荐结果，试试其他关键词</Text>
            )}
          </View>
        )}
      </View>

      {/* 学习路径卡片 */}
      {currentPath && (
        <View className={styles.section}>
          <View className={styles.sectionHeader}>
            <Text className={styles.sectionTitle}>我的学习路径</Text>
            <Text className={styles.sectionMore} onClick={handleViewPath}>查看全部 →</Text>
          </View>
          <PathCard path={currentPath} onClick={handleViewPath} />
        </View>
      )}

      {/* 分类筛选 */}
      <View className={styles.section}>
        <View className={styles.sectionHeader}>
          <Text className={styles.sectionTitle}>全部课程</Text>
        </View>
        <ScrollView className={styles.categoryScroll} scrollX>
          {categories.map((cat) => (
            <View
              key={cat.key}
              className={`${styles.categoryItem} ${activeCategory === cat.key ? styles.categoryActive : ''}`}
              onClick={() => handleCategoryChange(cat.key)}
            >
              <Text className={`${styles.categoryText} ${activeCategory === cat.key ? styles.categoryTextActive : ''}`}>
                {cat.label}
              </Text>
            </View>
          ))}
        </ScrollView>
      </View>

      {/* 课程列表 */}
      <View className={styles.courseList}>
        {courses.map((course) => (
          <View key={course.id} className={styles.courseItem}>
            <CourseCard course={course} onClick={() => handleViewCourse(course.id)} />
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default LearnPage;