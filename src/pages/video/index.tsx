import React, { useEffect, useState, useRef } from 'react';
import { View, Text, ScrollView, Image, Video } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { fetchVideos, fetchCourseDetail, completeVideo } from '@/services/api';
import { formatDuration } from '@/utils/index';
import type { Video as VideoType, Chapter } from '@/types/index';
import styles from './index.module.scss';

const IS_WEAPP = process.env.TARO_ENV === 'weapp';

/** 对可能 URL 编码的字符串做安全解码 */
const safeDecode = (s: string | undefined): string => {
  if (!s) return '';
  try {
    // 如果包含 % 编码字符，解码
    return /%[0-9A-Fa-f]{2}/.test(s) ? decodeURIComponent(s) : s;
  } catch {
    return s;
  }
};

/** 解析 Bilibili URL 的 BV ID 作为视频页的额外参考 */
const bvFromUrl = (url: string): string => {
  const m = url.match(/BV[0-9A-Za-z]{10}/);
  return m ? m[0] : '';
};

const VideoPage: React.FC = () => {
  const [videos, setVideos] = useState<VideoType[]>([]);
  const [currentVideo, setCurrentVideo] = useState<VideoType | null>(null);
  const [loading, setLoading] = useState(true);
  const [biliError, setBiliError] = useState(false);
  const [watchedLoading, setWatchedLoading] = useState(false);
  const iframeLoadedRef = useRef(false);
  const iframeTimerRef = useRef<any>(null);

  useEffect(() => {
    const loadVideos = async () => {
      try {
        const params = Taro.getCurrentInstance().router?.params || {};
        const { videoId, videoUrl, videoTitle, courseId, chapterId } = params as {
          videoId?: string; videoUrl?: string; videoTitle?: string;
          courseId?: string; chapterId?: string;
        };
        const allVideos = await fetchVideos(courseId || undefined);
        // 对所有视频字段做安全解码，修复 URL 编码中文导致的乱码
        const decodedVideos: VideoType[] = allVideos.map((v) => ({
          ...v,
          title: safeDecode(v.title),
          subtitle: safeDecode(v.subtitle || undefined),
          description: safeDecode(v.description),
          narrative: safeDecode(v.narrative || undefined),
          visual: safeDecode(v.visual || undefined),
          coreInfo: (v.coreInfo || []).map((s: string) => safeDecode(s)),
        }));
        setVideos(decodedVideos);

        // 如果传入了 videoUrl（来自章节视频按钮），查找对应课程章节获取中文标题和时长
        if (videoUrl) {
          const decodedUrl = decodeURIComponent(videoUrl);
          const decodedTitle = safeDecode(videoTitle);
          let chapterInfo: Chapter | null = null;
          let matchedFromList: VideoType | undefined;
          // 优先从已加载的视频列表匹配，获取完整元数据（subtitle、coreInfo、narrative等）
          if (decodedUrl) {
            // 章节跳转的 URL 可能与视频库 URL 的 page 参数不同（如 page=2 vs page=1），
            // 不能精确匹配整串 URL。改为按 bvid 匹配，确保拿到真实的 video id（用于"已看完"持久化）。
            const targetBv = bvFromUrl(decodedUrl);
            matchedFromList = targetBv
              ? decodedVideos.find((v) => bvFromUrl(v.url) === targetBv)
              : decodedVideos.find((v) => v.url === decodedUrl);
          }
          if (courseId) {
            try {
              const courseDetail = await fetchCourseDetail(courseId);
              chapterInfo =
                courseDetail?.chapters?.find(
                  (ch: any) => chapterId ? ch.id === chapterId : bvFromUrl(decodedUrl) === ch.video_bv,
                ) || null;
            } catch (_e) {
              // ignore
            }
          }
          if (matchedFromList) {
            // 已匹配到视频库中的记录，使用完整的解码后元数据
            setCurrentVideo({
              ...matchedFromList,
              title: (chapterInfo && safeDecode(chapterInfo.title)) || matchedFromList.title,
              description: (chapterInfo && safeDecode(chapterInfo.summary)) || matchedFromList.description,
              url: decodedUrl || matchedFromList.url,
              chapter: (chapterInfo && chapterInfo.id) || matchedFromList.chapter,
              courseId: courseId || matchedFromList.courseId,
            });
          } else {
            setCurrentVideo({
              id: 'external',
              title:
                (chapterInfo && safeDecode(chapterInfo.title)) ||
                decodedTitle ||
                '章节视频',
              subtitle: '',
              description:
                (chapterInfo && safeDecode(chapterInfo.summary)) ||
                '包含对应章节的完整讲解、案例演示与知识点梳理。',
              coreInfo: [],
              narrative: undefined,
              visual: undefined,
              quality: undefined,
              url: decodedUrl,
              coverUrl: chapterInfo ? '' : '',
              duration: (chapterInfo && chapterInfo.duration_minutes * 60) || 2700,
              chapter: (chapterInfo && chapterInfo.id) || chapterId || '',
              courseId: courseId || '',
            } as VideoType);
          }
          setLoading(false);
          return;
        }

        // 如果传入了 videoId，匹配对应视频；否则播第一个
        const target = videoId
          ? decodedVideos.find((v) => v.id === videoId)
          : decodedVideos[0];
        setCurrentVideo(target || decodedVideos[0] || null);
      } catch (err) {
        console.error('[Video] load error:', err);
      } finally {
        setLoading(false);
      }
    };
    loadVideos();
  }, []);

  /**
   * B站iframe加载状态监控：超时后自动切换到降级视图
   * 由于跨域iframe无法直接读取内部状态，通过注入onload标记+超时兜底
   */
  useEffect(() => {
    if (!currentVideo || !isBilibiliUrl(currentVideo.url) || biliError) return;
    iframeLoadedRef.current = false;
    // 清除前一个计时器
    if (iframeTimerRef.current) clearTimeout(iframeTimerRef.current);
    // 8秒后若仍未标记onload成功，则认为加载失败（B站反爬导致）
    iframeTimerRef.current = setTimeout(() => {
      if (!iframeLoadedRef.current) {
        console.warn('[Video] Bilibili iframe load timeout, fallback triggered');
        setBiliError(true);
      }
    }, 8000);
    return () => {
      if (iframeTimerRef.current) clearTimeout(iframeTimerRef.current);
    };
  }, [currentVideo?.id, currentVideo?.url]);

  const handleVideoClick = (video: VideoType) => {
    setCurrentVideo(video);
    setBiliError(false);
    iframeLoadedRef.current = false;
  };

  const handleMarkWatched = async () => {
    if (!currentVideo || watchedLoading) return;
    setWatchedLoading(true);
    try {
      await completeVideo(currentVideo.id);
      setCurrentVideo((prev) => (prev ? { ...prev, completed: true } : prev));
      Taro.showToast({ title: '已确认看完本视频', icon: 'success' });
    } catch (err) {
      console.error('[Video] mark watched failed:', err);
      Taro.showToast({ title: '确认失败，请重试', icon: 'none' });
    } finally {
      setWatchedLoading(false);
    }
  };

  const handleBack = () => {
    Taro.navigateBack();
  };

  /** 判断是否为 B 站嵌入 URL */
  const isBilibiliUrl = (url: string) => url.includes('player.bilibili.com');

  /** 切换到降级视图（手动触发） */
  const handleReportPlaybackIssue = () => {
    setBiliError(true);
  };

  /** 在 Bilibili 站点打开当前视频 */
  const handleOpenOnBilibili = () => {
    const bv = bvFromUrl(currentVideo?.url || '');
    const biliUrl = bv ? `https://www.bilibili.com/video/${bv}` : (currentVideo?.url || '');
    if (IS_WEAPP) {
      // 小程序：跳转到内置 web-view 页内嵌打开 B 站
      Taro.navigateTo({
        url: `/pages/webview/index?url=${encodeURIComponent(biliUrl)}`,
      });
    } else {
      window.open(biliUrl, '_blank');
    }
  };

  if (loading) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  if (!currentVideo) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>暂无视频</Text>
      </View>
    );
  }

  const isBilibili = isBilibiliUrl(currentVideo.url);

  return (
    <View className={styles.page}>
      {/* 顶部导航 */}
      <View className={styles.navBar}>
        <Text className={styles.navBack} onClick={handleBack}>← 返回</Text>
        <Text className={styles.navTitle}>视频播放</Text>
        <View className={styles.navRight} />
      </View>

      {/* 视频播放器 - 小程序端 B站用卡片引导，H5 用嵌入 */}
      <View className={styles.playerWrapper}>
        {isBilibili && IS_WEAPP ? (
          <View className={styles.weappBiliCard}>
            <View className={styles.weappBiliCardIcon}>🎬</View>
            <Text className={styles.weappBiliCardTitle}>{currentVideo.title}</Text>
            <Text className={styles.weappBiliCardDesc}>
              该视频来自 Bilibili，小程序内无法直接内嵌播放。请点击下方按钮前往 B 站观看，观看完成后回来标记已完成。
            </Text>
            <View className={styles.weappBiliCardBtn} onClick={handleOpenOnBilibili}>
              <Text className={styles.weappBiliCardBtnText}>在 Bilibili 观看 →</Text>
            </View>
          </View>
        ) : isBilibili ? (
          biliError ? (
            <View className={styles.biliFallback}>
              <Text className={styles.biliFallbackIcon}>▶</Text>
              <Text className={styles.biliFallbackText}>视频加载失败或受浏览器安全策略限制</Text>
              <Text className={styles.biliFallbackDesc}>
                推荐点击下方按钮，直接在 Bilibili 网站观看完整版视频
              </Text>
              <View className={styles.biliFallbackBtns}>
                <Text className={styles.biliFallbackLink} onClick={handleOpenOnBilibili}>
                  在 Bilibili 中打开 →
                </Text>
                <Text className={styles.biliFallbackRetry} onClick={() => { setBiliError(false); iframeLoadedRef.current = false; }}>
                  重试嵌入播放
                </Text>
              </View>
            </View>
          ) : (
            <View className={styles.biliWrapper}>
              <iframe
                className={styles.bilibiliPlayer}
                src={`${currentVideo.url}&autoplay=0&danmaku=0&t=0`}
                width="100%"
                height="100%"
                frameBorder="0"
                allowFullScreen
                allow="autoplay; fullscreen"
                style={{ border: 'none', borderRadius: 8 }}
                referrerPolicy="no-referrer"
                onLoad={() => { iframeLoadedRef.current = true; }}
              />
              <View className={styles.biliTroubleBar}>
                <Text className={styles.biliTroubleHint}>
                  {bvFromUrl(currentVideo.url)} · 无法播放？
                </Text>
                <Text className={styles.biliTroubleBtn} onClick={handleReportPlaybackIssue}>
                  切换备用方式
                </Text>
                <Text className={styles.biliTroubleBtnAlt} onClick={handleOpenOnBilibili}>
                  B站观看
                </Text>
              </View>
            </View>
          )
        ) : (
          <Video
            className={styles.videoPlayer}
            src={currentVideo.url}
            poster={currentVideo.coverUrl}
            controls
            autoplay
            enableProgressGesture
            showProgress
            showPlayBtn
            showCenterPlayBtn
          />
        )}
      </View>

      {/* 当前视频信息 */}
      <View className={styles.videoInfo}>
        <Text className={styles.videoTitle}>{currentVideo.title}</Text>
        {currentVideo.subtitle && (
          <Text className={styles.videoSubtitle}>{currentVideo.subtitle}</Text>
        )}
        <Text className={styles.videoDesc}>{currentVideo.description}</Text>
        <View className={styles.videoMetaLine}>
          <Text className={styles.videoDuration}>时长：{formatDuration(currentVideo.duration)}</Text>
          {currentVideo.quality && (
            <Text className={styles.videoQuality}>
              🎬 {currentVideo.quality.resolution} · {currentVideo.quality.fps}fps
            </Text>
          )}
        </View>

        {/* 核心知识点 */}
        {currentVideo.coreInfo && currentVideo.coreInfo.length > 0 && (
          <View className={styles.metaBlock}>
            <Text className={styles.metaLabel}>📌 核心信息</Text>
            {currentVideo.coreInfo.map((kp, i) => (
              <View key={i} className={styles.metaItem}>
                <Text className={styles.metaBullet}>•</Text>
                <Text className={styles.metaText}>{kp}</Text>
              </View>
            ))}
          </View>
        )}

        {/* 叙事结构 */}
        {currentVideo.narrative && (
          <View className={styles.metaBlockAlt}>
            <Text className={styles.metaLabelAlt}>🧭 叙事结构</Text>
            <Text className={styles.metaTextAlt}>{currentVideo.narrative}</Text>
          </View>
        )}

        {/* 视觉呈现 */}
        {currentVideo.visual && (
          <View className={styles.metaBlockAlt}>
            <Text className={styles.metaLabelAlt}>🎨 视觉呈现</Text>
            <Text className={styles.metaTextAlt}>{currentVideo.visual}</Text>
          </View>
        )}

        {/* 质量标准 */}
        {currentVideo.quality && (
          <View className={styles.qualityBar}>
            <View className={styles.qualityTag}><Text>清晰 {currentVideo.quality.resolution}</Text></View>
            <View className={styles.qualityTag}><Text>流畅 {currentVideo.quality.fps}fps</Text></View>
            <View className={styles.qualityTag}><Text>{currentVideo.quality.audio}</Text></View>
            <View className={styles.qualityTag}><Text>{currentVideo.quality.watermark}</Text></View>
          </View>
        )}

        {/* 看完确认按钮 */}
        <View
          className={`${styles.watchedBtn} ${currentVideo.completed ? styles.watchedBtnDone : ''}`}
          onClick={handleMarkWatched}
        >
          <Text className={styles.watchedBtnText}>
            {currentVideo.completed ? '✓ 已看完' : watchedLoading ? '确认中...' : '我已看完本视频'}
          </Text>
        </View>
      </View>

      {/* 视频列表标题 */}
      <View className={styles.listHeader}>
        <Text className={styles.listTitle}>播放列表</Text>
        <Text className={styles.listCount}>{videos.length} 个视频</Text>
      </View>

      {/* 视频列表 */}
      <ScrollView className={styles.videoList} scrollY>
        {videos.map((video) => (
          <View
            key={video.id}
            className={`${styles.videoItem} ${currentVideo.id === video.id ? styles.videoItemActive : ''}`}
            onClick={() => handleVideoClick(video)}
          >
            <Image className={styles.videoCover} src={video.coverUrl} mode="aspectFill" />
            <View className={styles.videoItemInfo}>
              <Text className={styles.videoItemTitle} numberOfLines={2}>{video.title}</Text>
              <Text className={styles.videoItemDuration}>{formatDuration(video.duration)}</Text>
            </View>
            {currentVideo.id === video.id && (
              <View className={styles.playingBadge}>
                <Text className={styles.playingBadgeText}>播放中</Text>
              </View>
            )}
          </View>
        ))}
      </ScrollView>
    </View>
  );
};

export default VideoPage;