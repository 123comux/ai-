import React from 'react';
import { View, Text } from '@tarojs/components';
import ProgressBar from '@/components/ProgressBar';
import type { LearningPath } from '@/types/index';
import styles from './index.module.scss';

interface PathCardProps {
  path: LearningPath;
  onClick?: () => void;
}

const PathCard: React.FC<PathCardProps> = ({ path, onClick }) => {
  const completedNodes = path.nodes.filter((n) => n.status === 'completed').length;
  const totalNodes = path.nodes.length;
  const percent = totalNodes > 0 ? Math.round((completedNodes / totalNodes) * 100) : 0;

  return (
    <View className={styles.card} onClick={onClick}>
      <View className={styles.header}>
        <View className={styles.directionBadge}>
          <Text className={styles.directionText}>{path.direction}</Text>
        </View>
      </View>
      <Text className={styles.title}>{path.title}</Text>
      <View className={styles.progressWrap}>
        <ProgressBar percent={percent} height={8} />
        <Text className={styles.progressText}>{completedNodes}/{totalNodes} 项</Text>
      </View>
    </View>
  );
};

export default PathCard;