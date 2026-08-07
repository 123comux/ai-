import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import ProgressBar from '@/components/ProgressBar';
import { fetchLearningPaths } from '@/services/api';
import type { LearningPath } from '@/types/index';
import styles from './index.module.scss';

const LearningPathPage: React.FC = () => {
  const [allPaths, setAllPaths] = useState<LearningPath[]>([]);
  const [activeId, setActiveId] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const paths = await fetchLearningPaths();
        setAllPaths(paths);
        // 默认选中第一个（推荐方向）
        setActiveId(paths[0]?.id || '');
      } catch (err) {
        console.error('[LearningPath] load error:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const currentPath = allPaths.find((p) => p.id === activeId) || allPaths[0] || null;

  const handleViewCourse = (courseId: string, node?: any) => {
    const pathId = currentPath?.id || '';
    const nodeId = node?.id || '';
    Taro.navigateTo({
      url: `/pages/courseDetail/index?id=${courseId}&pathId=${encodeURIComponent(pathId)}&nodeId=${encodeURIComponent(nodeId)}`,
    });
  };

  if (loading) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  if (!currentPath) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>暂无学习路径</Text>
      </View>
    );
  }

  const completedNodes = currentPath.nodes.filter((n) => n.status === 'completed').length;
  const totalNodes = currentPath.nodes.length;
  const percent = totalNodes > 0 ? Math.round((completedNodes / totalNodes) * 100) : 0;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'current': return '🟦';
      case 'locked': return '🔒';
      default: return '⬜';
    }
  };

  return (
    <ScrollView className={styles.page} scrollY>
      <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
        <Text className={styles.navBack}>← 返回</Text>
      </View>
      <View className={styles.section}>
        <View className={styles.headerInfo}>
          <Text className={styles.direction}>{currentPath.direction}</Text>
          <Text className={styles.title}>{currentPath.title}</Text>
          <View className={styles.progressInfo}>
            <Text className={styles.progressText}>
              第 {currentPath.currentWeek}/{currentPath.totalWeeks} 周
            </Text>
            <Text className={styles.progressText}>
              {completedNodes}/{totalNodes} 项完成
            </Text>
          </View>
          <ProgressBar percent={percent} height={8} />
        </View>
      </View>

      {/* 方向切换 tab */}
      <Text className={styles.sectionTitle}>选择学习方向</Text>
      <View className={styles.directionTabs}>
        {allPaths.map((path) => (
          <View
            key={path.id}
            className={`${styles.directionTab} ${path.id === currentPath.id ? styles.directionTabActive : ''}`}
            onClick={() => setActiveId(path.id)}
          >
            <Text>{path.direction}</Text>
          </View>
        ))}
      </View>

      <Text className={styles.sectionTitle}>学习路径</Text>
      <View className={styles.pathList}>
        {currentPath.nodes.map((node, index) => (
          <View key={node.id} className={styles.pathItem}>
            <View className={styles.pathLine}>
              <View className={styles.pathDot}>
                <Text className={styles.pathDotIcon}>{getStatusIcon(node.status)}</Text>
              </View>
              {index < currentPath.nodes.length - 1 && (
                <View className={styles.pathConnector} />
              )}
            </View>
            <View
              className={styles.pathContent}
              onClick={() => {
                if (node.status === 'locked') {
                  Taro.showToast({ title: '请先完成前一节点', icon: 'none' });
                  return;
                }
                if (node.courseId) {
                  handleViewCourse(node.courseId, node);
                }
              }}
            >
              <Text className={styles.pathTitle}>{node.title}</Text>
              <Text className={styles.pathType}>
                {node.type === 'course' ? '📚 课程' : '🛠️ 项目'}
              </Text>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default LearningPathPage;