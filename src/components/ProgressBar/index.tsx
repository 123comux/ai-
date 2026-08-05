import React from 'react';
import { View } from '@tarojs/components';
import classnames from 'classnames';
import styles from './index.module.scss';

interface ProgressBarProps {
  percent: number;
  height?: number;
  color?: string;
  className?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  percent,
  height = 8,
  color,
  className,
}) => {
  const clampedPercent = Math.min(100, Math.max(0, percent));

  return (
    <View
      className={classnames(styles.progressBar, className)}
      style={{ height: `${height}rpx` }}
    >
      <View
        className={styles.fill}
        style={{
          width: `${clampedPercent}%`,
          backgroundColor: color,
          height: `${height}rpx`,
        }}
      />
    </View>
  );
};

export default ProgressBar;