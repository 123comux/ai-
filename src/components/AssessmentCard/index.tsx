import React from 'react';
import { View, Text } from '@tarojs/components';
import styles from './index.module.scss';

interface AssessmentCardProps {
  overallScore: number;
  level: string;
  direction: string;
  onClick?: () => void;
}

const AssessmentCard: React.FC<AssessmentCardProps> = ({
  overallScore,
  level,
  direction,
  onClick,
}) => {
  return (
    <View className={styles.card} onClick={onClick}>
      <View className={styles.header}>
        <Text className={styles.title}>AI 能力测评</Text>
        <View className={styles.badge}>
          <Text className={styles.badgeText}>已测评</Text>
        </View>
      </View>
      <View className={styles.content}>
        <View className={styles.scoreWrap}>
          <Text className={styles.scoreValue}>{overallScore}</Text>
          <Text className={styles.scoreUnit}>分</Text>
        </View>
        <View className={styles.info}>
          <View className={styles.infoItem}>
            <Text className={styles.infoLabel}>当前水平</Text>
            <Text className={styles.infoValue}>{level}</Text>
          </View>
          <View className={styles.infoItem}>
            <Text className={styles.infoLabel}>推荐方向</Text>
            <Text className={styles.infoValueHighlight}>{direction}</Text>
          </View>
        </View>
      </View>
    </View>
  );
};

export default AssessmentCard;