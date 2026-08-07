import React, { useEffect, useState } from 'react';
import { View, Text, Image, ScrollView } from '@tarojs/components';
import Taro, { useDidShow } from '@tarojs/taro';
import RadarChart from '@/components/RadarChart';
import { useUserStore } from '@/store/useUserStore';
import { fetchAbilityReport, fetchLearningRecords, fetchLearningStats, fetchMenuItems } from '@/services/api';
import type { LearningRecord } from '@/types/index';
import type { MenuItem } from '@/services/api';
import styles from './index.module.scss';

const MinePage: React.FC = () => {
  const { nickname, avatar, grade, major, targetDirection } = useUserStore();
  const [abilityReport, setAbilityReport] = useState<any>(null);
  const [records, setRecords] = useState<LearningRecord[]>([]);
  const [stats, setStats] = useState({ learningDays: 0, totalMinutes: 0, completedProjects: 0, completedLessons: 0 });
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);

  const loadData = async () => {
    try {
      const [reportData, recordData, statsData, menuData] = await Promise.all([
        fetchAbilityReport(),
        fetchLearningRecords(),
        fetchLearningStats(),
        fetchMenuItems('mine'),
      ]);
      setAbilityReport(reportData);
      setRecords(recordData);
      setStats(statsData);
      setMenuItems(menuData);
    } catch (err) {
      console.error('[Mine] load data error:', err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 每次显示刷新，学习时长/能力报告同步
  useDidShow(() => {
    loadData();
  });

  const handleMenuClick = (item: MenuItem) => {
    if (item.path) {
      Taro.navigateTo({ url: item.path });
    } else {
      Taro.showToast({ title: '功能开发中', icon: 'none' });
    }
  };

  return (
    <ScrollView className={styles.page} scrollY>
      {/* 用户信息头部 */}
      <View className={styles.header}>
        <View className={styles.headerBg} />
        <View className={styles.userInfo}>
          <Image className={styles.avatar} src={avatar} mode="aspectFill" />
          <Text className={styles.nickname}>{nickname}</Text>
        </View>
      </View>

      {/* 学习统计 */}
      <View className={styles.statsRow}>
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{stats.learningDays}</Text>
          <Text className={styles.statLabel}>学习天数</Text>
        </View>
        <View className={styles.statDivider} />
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{stats.totalMinutes}</Text>
          <Text className={styles.statLabel}>学习时长(min)</Text>
        </View>
        <View className={styles.statDivider} />
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{stats.completedLessons}</Text>
          <Text className={styles.statLabel}>完成课程</Text>
        </View>
        <View className={styles.statDivider} />
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{stats.completedProjects}</Text>
          <Text className={styles.statLabel}>完成项目</Text>
        </View>
      </View>

      {/* 能力报告 */}
      {abilityReport && (
        <View className={styles.section}>
          <View className={styles.sectionHeader}>
            <Text className={styles.sectionTitle}>能力报告</Text>
            <Text className={styles.sectionMore} onClick={() => Taro.navigateTo({ url: '/pages/assessment/index' })}>
              查看详情 →
            </Text>
          </View>
          <View className={styles.reportCard}>
            <RadarChart dimensions={abilityReport.dimensions} size={400} />
            <View className={styles.reportInfo}>
              <View className={styles.reportRow}>
                <Text className={styles.reportLabel}>综合评分</Text>
                <Text className={styles.reportValue}>{abilityReport.overallScore} 分</Text>
              </View>
              <View className={styles.reportRow}>
                <Text className={styles.reportLabel}>当前水平</Text>
                <Text className={styles.reportValue}>{abilityReport.level}</Text>
              </View>
              <View className={styles.reportRow}>
                <Text className={styles.reportLabel}>推荐方向</Text>
                <Text className={styles.reportValueHighlight}>{abilityReport.recommendedDirection}</Text>
              </View>
            </View>
          </View>
        </View>
      )}

      {/* 学习记录 */}
      <View className={styles.section}>
        <View className={styles.sectionHeader}>
          <Text className={styles.sectionTitle}>最近学习</Text>
        </View>
        <View className={styles.recordList}>
          {records.slice(0, 5).map((record, index) => (
            <View key={index} className={styles.recordItem}>
              <Text className={styles.recordDate}>{record.date}</Text>
              <View className={styles.recordBar}>
                <View
                  className={styles.recordFill}
                  style={{ width: `${(record.duration / 80) * 100}%` }}
                />
              </View>
              <Text className={styles.recordDuration}>{record.duration}分钟</Text>
            </View>
          ))}
        </View>
      </View>

      {/* 功能菜单 */}
      <View className={styles.menuSection}>
        {menuItems.map((item, index) => (
          <View
            key={index}
            className={styles.menuItem}
            onClick={() => handleMenuClick(item)}
          >
            <Text className={styles.menuIcon}>{item.icon}</Text>
            <Text className={styles.menuLabel}>{item.label}</Text>
            <Text className={styles.menuArrow}>→</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default MinePage;