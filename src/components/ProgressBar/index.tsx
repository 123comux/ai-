import React from 'react';
import { View } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';

const IS_WEAPP = process.env.TARO_ENV === 'weapp';

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

  // 高度单位必须分端处理：小程序端 rpx 是原生单位，直接用 `${height}rpx`；
  // H5 端行内样式里的 rpx 不是合法 CSS 单位，浏览器会整条丢弃（进度条高度变 0、看不见），
  // 所以用 Taro.pxTransform 换算成 rem——与样式表里 rpx 的换算规则完全一致
  // （H5 端同为 size/37.5 rem，配合 index.html 里锁定的 18px 根字号）。
  const barHeight = IS_WEAPP ? `${height}rpx` : Taro.pxTransform(height);

  return (
    <View
      className={classnames(styles.progressBar, className)}
      style={{ height: barHeight }}
    >
      <View
        className={styles.fill}
        style={{
          width: `${clampedPercent}%`,
          backgroundColor: color,
          height: barHeight,
        }}
      />
    </View>
  );
};

export default ProgressBar;
