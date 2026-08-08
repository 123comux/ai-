import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { fetchLearningRecords } from '@/services/api';
import type { LearningRecord } from '@/types/index';
import styles from './index.module.scss';

const LearningRecordPage: React.FC = () => {
  const [records, setRecords] = useState<LearningRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchLearningRecords();
        setRecords(data);
      } catch (err) {
        console.error('[LearningRecord] load error:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const totalMinutes = records.reduce((sum, r) => sum + (r.duration || 0), 0);
  const totalLessons = records.reduce((sum, r) => sum + (r.lessonsCompleted || 0), 0);
  const totalDays = records.length;
  const maxDuration = Math.max(1, ...records.map((r) => r.duration || 0));

  if (loading) {
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

      <View className={styles.summary}>
        <View className={styles.summaryItem}>
          <Text className={styles.summaryValue}>{totalMinutes}</Text>
          <Text className={styles.summaryLabel}>累计时长(min)</Text>
        </View>
        <View className={styles.summaryItem}>
          <Text className={styles.summaryValue}>{totalLessons}</Text>
          <Text className={styles.summaryLabel}>完成小节</Text>
        </View>
        <View className={styles.summaryItem}>
          <Text className={styles.summaryValue}>{totalDays}</Text>
          <Text className={styles.summaryLabel}>学习天数</Text>
        </View>
      </View>

      {records.length === 0 ? (
        <View className={styles.empty}>
          <Text className={styles.emptyIcon}>📝</Text>
          <Text className={styles.emptyText}>还没有学习记录，开始学习吧</Text>
        </View>
      ) : (
        <View className={styles.list}>
          {records.map((record, index) => (
            <View key={index} className={styles.item}>
              <Text className={styles.date}>{record.date}</Text>
              <View className={styles.barWrap}>
                <View className={styles.bar}>
                  <View
                    className={styles.fill}
                    style={{ width: `${Math.round(((record.duration || 0) / maxDuration) * 100)}%` }}
                  />
                </View>
                <Text className={styles.lessonCount}>{record.lessonsCompleted} 节视频</Text>
              </View>
              <Text className={styles.duration}>{record.duration}分</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
};

export default LearningRecordPage;
