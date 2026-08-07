import React, { useEffect, useRef } from 'react';
import { View, Canvas } from '@tarojs/components';
import Taro from '@tarojs/taro';
import type { AbilityDimension } from '@/types/index';
import styles from './index.module.scss';

interface RadarChartProps {
  dimensions: AbilityDimension[];
  size?: number;
}

const IS_WEAPP = process.env.TARO_ENV === 'weapp';

const RadarChart: React.FC<RadarChartProps> = ({ dimensions, size = 500 }) => {
  const canvasId = useRef(`radar-${Math.random().toString(36).slice(2, 9)}`).current;

  // 小程序端：Canvas 绘制（用 createCanvasContext 经典 API，稳定跨端）
  useEffect(() => {
    if (!IS_WEAPP || !dimensions || dimensions.length === 0) return;

    // canvas CSS 为 500rpx，绘制坐标单位是 px，需换算成实际像素尺寸
    // （750rpx = 屏宽 px，故 500rpx = 500/750 * 屏宽px），否则绘制内容与显示尺寸不匹配被裁切
    let pxSize = 250; // 兜底：375px 屏上 500rpx ≈ 250px
    try {
      const sys = Taro.getSystemInfoSync();
      if (sys && typeof sys.windowWidth === 'number' && sys.windowWidth > 0) {
        pxSize = (500 * sys.windowWidth) / 750;
      }
    } catch (e) {
      // 系统信息获取失败时使用默认值，避免阻断页面渲染
    }

    const draw = () => {
      try {
        const ctx = Taro.createCanvasContext(canvasId);
        const size = pxSize;
        const center = size / 2;
        // 半径按比例取 size 的 36%，与 H5 端（radius=size/2-60，size=400 时占 35%）视觉一致
        const radius = size * 0.36;
        const angleStep = (Math.PI * 2) / dimensions.length;

        const getPoint = (index: number, ratio: number) => {
          const angle = angleStep * index - Math.PI / 2;
          const r = radius * ratio;
        return { x: center + r * Math.cos(angle), y: center + r * Math.sin(angle) };
      };

      ctx.setStrokeStyle('#e5e6eb');
      ctx.setLineWidth(2);
      for (let level = 0.25; level <= 1; level += 0.25) {
        ctx.beginPath();
        dimensions.forEach((_, i) => {
          const p = getPoint(i, level);
          if (i === 0) ctx.moveTo(p.x, p.y);
          else ctx.lineTo(p.x, p.y);
        });
        ctx.closePath();
        ctx.stroke();
      }
      dimensions.forEach((_, i) => {
        const p = getPoint(i, 1);
        ctx.beginPath();
        ctx.moveTo(center, center);
        ctx.lineTo(p.x, p.y);
        ctx.stroke();
      });
      ctx.beginPath();
      dimensions.forEach((dim, i) => {
        const ratio = dim.maxScore > 0 ? dim.score / dim.maxScore : 0;
        const p = getPoint(i, ratio);
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      });
      ctx.closePath();
      ctx.setFillStyle('rgba(22, 93, 255, 0.15)');
      ctx.fill();
      ctx.setStrokeStyle('#165dff');
      ctx.setLineWidth(3);
      ctx.stroke();
      dimensions.forEach((dim, i) => {
        const ratio = dim.maxScore > 0 ? dim.score / dim.maxScore : 0;
        const p = getPoint(i, ratio);
        ctx.beginPath();
        ctx.arc(p.x, p.y, 6, 0, Math.PI * 2);
        ctx.setFillStyle('#165dff');
        ctx.fill();
      });
      ctx.setFillStyle('#4e5969');
      ctx.setTextAlign('center');
      ctx.setTextBaseline('middle');
      ctx.setFontSize(14);
      dimensions.forEach((dim, i) => {
        const p = getPoint(i, 1.18);
        ctx.fillText(dim.label, p.x, p.y);
      });
      ctx.draw();
      } catch (e) {
        // Canvas 绘制异常不阻断页面渲染
        console.error('[RadarChart] draw error:', e);
      }
    };

    const t1 = setTimeout(draw, 100);
    const t2 = setTimeout(draw, 400);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [dimensions, size, canvasId]);

  // H5 端：SVG 绘制（小程序不支持 svg）
  if (!IS_WEAPP) {
    if (!dimensions || dimensions.length === 0) return null;
    const center = size / 2;
    const radius = size / 2 - 60;
    const angleStep = (Math.PI * 2) / dimensions.length;
    const getPoint = (index: number, value: number, maxValue: number) => {
      const angle = angleStep * index - Math.PI / 2;
      const r = (value / maxValue) * radius;
      return { x: center + r * Math.cos(angle), y: center + r * Math.sin(angle) };
    };
    const gridLevels = [0.25, 0.5, 0.75, 1];
    const gridLines = gridLevels.map((level) =>
      dimensions.map((_, i) => getPoint(i, level, 1))
    );
    const dataPoints = dimensions.map((dim, i) => getPoint(i, dim.score, dim.maxScore));

    return (
      <View className={styles.chart}>
        <svg viewBox={`0 0 ${size} ${size}`} width="100%" height="100%">
          {gridLines.map((points, gi) => (
            <polygon
              key={gi}
              points={points.map((p) => `${p.x},${p.y}`).join(' ')}
              fill="none"
              stroke="#e5e6eb"
              strokeWidth="2"
            />
          ))}
          {dimensions.map((_, i) => {
            const p = getPoint(i, 1, 1);
            return (
              <line key={i} x1={center} y1={center} x2={p.x} y2={p.y} stroke="#e5e6eb" strokeWidth="2" />
            );
          })}
          <polygon
            points={dataPoints.map((p) => `${p.x},${p.y}`).join(' ')}
            fill="rgba(22, 93, 255, 0.15)"
            stroke="#165dff"
            strokeWidth="3"
          />
          {dataPoints.map((p, i) => (
            <circle key={i} cx={p.x} cy={p.y} r="6" fill="#165dff" />
          ))}
          {dimensions.map((dim, i) => {
            const p = getPoint(i, 1.18, 1);
            return (
              <text key={i} x={p.x} y={p.y} textAnchor="middle" dominantBaseline="middle" fill="#4e5969" fontSize="28" fontWeight="500">
                {dim.label}
              </text>
            );
          })}
        </svg>
      </View>
    );
  }

  // 小程序端：Canvas
  return (
    <View className={styles.chart}>
      <Canvas
        canvasId={canvasId}
        className={styles.canvas}
      />
    </View>
  );
};

export default RadarChart;
