import React from 'react';
import { View, Text, Image } from '@tarojs/components';
import ProgressBar from '@/components/ProgressBar';
import { formatDuration } from '@/utils/index';
import type { Course } from '@/types/index';
import styles from './index.module.scss';

interface CourseCardProps {
  course: Course;
  onClick?: () => void;
}

const CourseCard: React.FC<CourseCardProps> = ({ course, onClick }) => {
  return (
    <View className={styles.card} onClick={onClick}>
      <Image
        className={styles.cover}
        src={course.coverImg}
        mode="aspectFill"
      />
      <View className={styles.body}>
        <Text className={styles.title}>{course.title}</Text>
        <Text className={styles.desc}>{course.description}</Text>
        <View className={styles.meta}>
          <Text className={styles.metaText}>
            {course.lessons}节 · {formatDuration(course.duration)}
          </Text>
          {!course.isFree && (
            <View className={styles.proTag}>
              <Text className={styles.proTagText}>PRO</Text>
            </View>
          )}
        </View>
        {course.progress > 0 && (
          <View className={styles.progressWrap}>
            <ProgressBar percent={course.progress} height={6} />
            <Text className={styles.progressText}>{course.progress}%</Text>
          </View>
        )}
      </View>
    </View>
  );
};

export default CourseCard;