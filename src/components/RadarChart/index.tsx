import React from 'react';
import { View, Text } from '@tarojs/components';
import type { AbilityDimension } from '@/types/index';
import styles from './index.module.scss';

interface RadarChartProps {
  dimensions: AbilityDimension[];
  size?: number;
}

const RadarChart: React.FC<RadarChartProps> = ({ dimensions, size = 500 }) => {
  const center = size / 2;
  const radius = size / 2 - 60;
  const angleStep = (Math.PI * 2) / dimensions.length;

  // 计算每个顶点的坐标
  const getPoint = (index: number, value: number, maxValue: number) => {
    const angle = angleStep * index - Math.PI / 2;
    const r = (value / maxValue) * radius;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    };
  };

  // 生成网格线（3层）
  const gridLevels = [0.25, 0.5, 0.75, 1];
  const gridLines = gridLevels.map((level) => {
    const points = dimensions.map((_, i) => {
      const angle = angleStep * i - Math.PI / 2;
      const r = radius * level;
      return { x: center + r * Math.cos(angle), y: center + r * Math.sin(angle) };
    });
    return points;
  });

  // 数据多边形
  const dataPoints = dimensions.map((dim, i) => {
    const angle = angleStep * i - Math.PI / 2;
    const r = (dim.score / dim.maxScore) * radius;
    return { x: center + r * Math.cos(angle), y: center + r * Math.sin(angle) };
  });

  const dataPath = dataPoints.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ') + 'Z';

  return (
    <View className={styles.chart} style={{ width: `${size / 2.5}rpx`, height: `${size / 2.5}rpx` }}>
      <svg viewBox={`0 0 ${size} ${size}`} width="100%" height="100%">
        {/* 网格线 */}
        {gridLines.map((points, gi) => (
          <polygon
            key={gi}
            points={points.map((p) => `${p.x},${p.y}`).join(' ')}
            fill="none"
            stroke="#e5e6eb"
            strokeWidth="2"
          />
        ))}
        {/* 轴线 */}
        {dimensions.map((_, i) => {
          const p = getPoint(i, 1, 1);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={p.x}
              y2={p.y}
              stroke="#e5e6eb"
              strokeWidth="2"
            />
          );
        })}
        {/* 数据多边形 */}
        <polygon
          points={dataPoints.map((p) => `${p.x},${p.y}`).join(' ')}
          fill="rgba(22, 93, 255, 0.15)"
          stroke="#165dff"
          strokeWidth="3"
        />
        {/* 数据点 */}
        {dataPoints.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="6" fill="#165dff" />
        ))}
        {/* 标签 */}
        {dimensions.map((dim, i) => {
          const p = getPoint(i, 1.18, 1);
          return (
            <text
              key={i}
              x={p.x}
              y={p.y}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#4e5969"
              fontSize="28"
              fontWeight="500"
            >
              {dim.label}
            </text>
          );
        })}
      </svg>
    </View>
  );
};

export default RadarChart;