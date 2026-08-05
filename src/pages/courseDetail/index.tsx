import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Image } from '@tarojs/components';
import Taro from '@tarojs/taro';
import ProgressBar from '@/components/ProgressBar';
import { fetchCourses } from '@/services/api';
import { formatDuration } from '@/utils/index';
import type { Course } from '@/types/index';
import styles from './index.module.scss';

const CourseDetailPage: React.FC = () => {
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCourse = async () => {
      try {
        const { id } = Taro.getCurrentInstance().router?.params || {};
        const courses = await fetchCourses();
        const found = courses.find((c) => c.id === id);
        setCourse(found || null);
      } catch (err) {
        console.error('[CourseDetail] load error:', err);
      } finally {
        setLoading(false);
      }
    };
    loadCourse();
  }, []);

  if (loading) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  if (!course) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>课程不存在</Text>
      </View>
    );
  }

  const chapters = [
    { id: 1, title: '第一章：课程介绍与环境搭建', duration: '15分钟', status: 'completed' },
    { id: 2, title: '第二章：核心概念讲解', duration: '25分钟', status: 'completed' },
    { id: 3, title: '第三章：基础语法与实战', duration: '30分钟', status: 'current' },
    { id: 4, title: '第四章：进阶技巧', duration: '35分钟', status: 'locked' },
    { id: 5, title: '第五章：项目实战', duration: '40分钟', status: 'locked' },
    { id: 6, title: '第六章：总结与拓展', duration: '20分钟', status: 'locked' },
  ];

  return (
    <ScrollView className={styles.page} scrollY>
      <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
        <Text className={styles.navBack}>← 返回</Text>
      </View>
      <Image className={styles.cover} src={course.coverImg} mode="aspectFill" />
      <View className={styles.body}>
        <Text className={styles.title}>{course.title}</Text>
        <Text className={styles.desc}>{course.description}</Text>
        <View className={styles.meta}>
          <Text className={styles.metaText}>{course.lessons} 节课程</Text>
          <Text className={styles.metaDot}>·</Text>
          <Text className={styles.metaText}>{formatDuration(course.duration)}</Text>
          {!course.isFree && (
            <>
              <Text className={styles.metaDot}>·</Text>
              <Text className={styles.proText}>PRO 课程</Text>
            </>
          )}
        </View>
        <View className={styles.progressSection}>
          <View className={styles.progressHeader}>
            <Text className={styles.progressLabel}>学习进度</Text>
            <Text className={styles.progressValue}>{course.progress}%</Text>
          </View>
          <ProgressBar percent={course.progress} height={8} />
        </View>

        <Text className={styles.sectionTitle}>课程目录</Text>
        <View className={styles.chapterList}>
          {chapters.map((ch) => (
            <View key={ch.id} className={styles.chapterItem}>
              <View className={styles.chapterStatus}>
                {ch.status === 'completed' && <Text className={styles.statusIcon}>✅</Text>}
                {ch.status === 'current' && <View className={styles.currentDot} />}
                {ch.status === 'locked' && <Text className={styles.statusIcon}>🔒</Text>}
              </View>
              <View className={styles.chapterInfo}>
                <Text className={styles.chapterTitle}>{ch.title}</Text>
                <Text className={styles.chapterDuration}>{ch.duration}</Text>
              </View>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );
};

export default CourseDetailPage;