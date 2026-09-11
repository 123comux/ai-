import React from 'react';
import { View, Text, Image } from '@tarojs/components';
import classnames from 'classnames';
import ProgressBar from '@/components/ProgressBar';
import { getDifficultyLabel } from '@/utils/index';
import type { Project } from '@/types/index';
import styles from './index.module.scss';

interface ProjectCardProps {
  project: Project;
  onClick?: () => void;
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project, onClick }) => {
  return (
    <View
      className={classnames(styles.card, project.status === 'locked' && styles.locked)}
      onClick={onClick}
    >
      <View className={styles.coverWrap}>
        <Image className={styles.cover} src={project.coverImg} mode="aspectFill" />
        {project.status === 'locked' && (
          <View className={styles.lockOverlay}>
            <Text className={styles.lockIcon}>完成前置项目后解锁</Text>
          </View>
        )}
      </View>
      <View className={styles.body}>
        <Text className={styles.title}>{project.title}</Text>
        <Text className={styles.desc}>{project.description}</Text>
        <View className={styles.tags}>
          <View className={styles.tag}>
            <Text className={styles.tagText}>
              {getDifficultyLabel(project.difficulty)}
            </Text>
          </View>
          <View className={styles.tag}>
            <Text className={styles.tagText}>{project.estimatedHours}h</Text>
          </View>
          {project.isFree ? (
            <View className={styles.freeTag}>
              <Text className={styles.freeTagText}>免费</Text>
            </View>
          ) : (
            <View className={styles.proTag}>
              <Text className={styles.proTagText}>¥{project.price}</Text>
            </View>
          )}
        </View>
        {project.progress > 0 && (
          <View className={styles.progressWrap}>
            <ProgressBar percent={project.progress} height={6} />
            <Text className={styles.progressText}>{project.progress}%</Text>
          </View>
        )}
      </View>
    </View>
  );
};

export default ProjectCard;