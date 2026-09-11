/**
 * 通用 UI 原语（单一模块，22 个页面复用）
 *
 * 设计约定：
 * - 全部尺寸/颜色走 token（src/styles/theme.scss），因此**换主题只改 token 文件**，组件零返工。
 * - 移动端尺寸 rpx；桌面覆盖用大写 PX（pxtransform 不换算大写单位）。
 * - 交互状态齐全：hover / :active 按压 / focus-visible 焦点环 / disabled / loading。
 * - Reveal 的动效仅在 H5 执行（process.env.TARO_ENV 在编译期被 Taro 替换，小程序端整段被摇掉）。
 */
import { useEffect, useRef, useState } from 'react';
import { View, Text } from '@tarojs/components';
import styles from './index.module.scss';

type Tone = 'primary' | 'ghost' | 'subtle' | 'danger';

export function Button({
  children,
  onClick,
  tone = 'primary',
  size = 'md',
  block,
  disabled,
  loading,
  className = ''
}: {
  children?: React.ReactNode;
  onClick?: () => void;
  tone?: Tone;
  size?: 'sm' | 'md' | 'lg';
  block?: boolean;
  disabled?: boolean;
  loading?: boolean;
  className?: string;
}) {
  return (
    <View
      className={[
        styles.btn,
        styles[`btn_${tone}`],
        styles[`btn_${size}`],
        block ? styles.btnBlock : '',
        disabled || loading ? styles.btnDisabled : '',
        className
      ]
        .filter(Boolean)
        .join(' ')}
      onClick={() => {
        if (disabled || loading) return;
        onClick?.();
      }}
      role="button"
      aria-disabled={disabled || loading ? 'true' : undefined}
      tabIndex={0}
    >
      {loading ? <View className={styles.btnSpinner} /> : null}
      <Text className={styles.btnLabel}>{children}</Text>
    </View>
  );
}

export function Panel({
  children,
  className = '',
  spotlight,
  padded = true,
  as: _as
}: {
  children?: React.ReactNode;
  className?: string;
  /** 开启光标跟随描边（H5 桌面端） */
  spotlight?: boolean;
  padded?: boolean;
  as?: string;
}) {
  const ref = useRef<HTMLElement | null>(null);
  useEffect(() => {
    if (!spotlight || process.env.TARO_ENV !== 'h5') return;
    const el = ref.current as unknown as HTMLElement | null;
    if (!el) return;
    const onMove = (e: PointerEvent) => {
      const r = el.getBoundingClientRect();
      el.style.setProperty('--mx', `${e.clientX - r.left}px`);
      el.style.setProperty('--my', `${e.clientY - r.top}px`);
    };
    el.addEventListener('pointermove', onMove);
    return () => el.removeEventListener('pointermove', onMove);
  }, [spotlight]);

  return (
    <View
      // @ts-ignore Taro 的 View 会透传 ref 到宿主节点
      ref={ref}
      className={[styles.panel, padded ? styles.panelPadded : '', spotlight ? styles.panelSpotlight : '', className]
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </View>
  );
}

export function Tag({ children, tone = 'neutral' }: { children?: React.ReactNode; tone?: 'neutral' | 'accent' | 'success' | 'warning' }) {
  return (
    <View className={`${styles.tag} ${styles[`tag_${tone}`]}`}>
      <Text>{children}</Text>
    </View>
  );
}

export function SectionHeader({
  title,
  hint,
  actionText,
  onAction
}: {
  title: string;
  hint?: string;
  actionText?: string;
  onAction?: () => void;
}) {
  return (
    <View className={styles.sectionHeader}>
      <View className={styles.sectionTitleWrap}>
        <Text className={styles.sectionTitle}>{title}</Text>
        {hint ? <Text className={styles.sectionHint}>{hint}</Text> : null}
      </View>
      {actionText ? (
        <View className={styles.sectionAction} onClick={onAction} role="button" tabIndex={0}>
          <Text>{actionText}</Text>
          <Text className={styles.sectionActionArrow}>→</Text>
        </View>
      ) : null}
    </View>
  );
}

export function Stat({ value, label, hint }: { value: React.ReactNode; label: string; hint?: string }) {
  return (
    <View className={styles.stat}>
      <Text className={styles.statValue}>{value}</Text>
      <Text className={styles.statLabel}>{label}</Text>
      {hint ? <Text className={styles.statHint}>{hint}</Text> : null}
    </View>
  );
}

export function Skeleton({ height = 120, radius = 12, className = '' }: { height?: number; radius?: number; className?: string }) {
  return (
    <View
      className={`${styles.skeleton} ${className}`}
      style={{ height: `${height}rpx`, borderRadius: `${radius}rpx` }}
    />
  );
}

export function EmptyState({
  title,
  desc,
  actionText,
  onAction,
  tone = 'neutral'
}: {
  title: string;
  desc?: string;
  actionText?: string;
  onAction?: () => void;
  tone?: 'neutral' | 'error';
}) {
  return (
    <View className={`${styles.empty} ${tone === 'error' ? styles.emptyError : ''}`}>
      <View className={styles.emptyGlyph} aria-hidden />
      <Text className={styles.emptyTitle}>{title}</Text>
      {desc ? <Text className={styles.emptyDesc}>{desc}</Text> : null}
      {actionText ? (
        <Button tone="ghost" size="sm" onClick={onAction}>
          {actionText}
        </Button>
      ) : null}
    </View>
  );
}

/**
 * Reveal：进入视口时上浮淡入（H5 桌面/移动都可用；小程序端直接返回 children）。
 * 用 IntersectionObserver 而不是 scroll 事件；尊重 prefers-reduced-motion。
 */
export function Reveal({
  children,
  delay = 0,
  className = ''
}: {
  children?: React.ReactNode;
  delay?: number;
  className?: string;
}) {
  const ref = useRef<HTMLElement | null>(null);
  const [shown, setShown] = useState(process.env.TARO_ENV !== 'h5');

  useEffect(() => {
    if (process.env.TARO_ENV !== 'h5') return;
    const el = ref.current as unknown as HTMLElement | null;
    if (!el) return;
    if (typeof IntersectionObserver === 'undefined') {
      setShown(true);
      return;
    }
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    if (reduce) {
      setShown(true);
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setShown(true);
            io.disconnect();
          }
        });
      },
      { rootMargin: '0px 0px -12% 0px', threshold: 0.06 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <View
      // @ts-ignore
      ref={ref}
      className={`${styles.reveal} ${shown ? styles.revealIn : ''} ${className}`}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
    >
      {children}
    </View>
  );
}
