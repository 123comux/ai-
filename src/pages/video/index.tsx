import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Image, Video } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { fetchVideos } from '@/services/api';
import { formatDuration } from '@/utils/index';
import type { Video as VideoType } from '@/types/index';
import styles from './index.module.scss';

const VideoPage: React.FC = () => {
  const [videos, setVideos] = useState<VideoType[]>([]);
  const [currentVideo, setCurrentVideo] = useState<VideoType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadVideos = async () => {
      try {
        const { videoId } = Taro.getCurrentInstance().router?.params || {};
        const allVideos = await fetchVideos();
        setVideos(allVideos);

        // 如果传入了 videoId，默认播放该视频；否则播第一个
        const target = videoId
          ? allVideos.find((v) => v.id === videoId)
          : allVideos[0];
        setCurrentVideo(target || allVideos[0] || null);
      } catch (err) {
        console.error('[Video] load error:', err);
      } finally {
        setLoading(false);
      }
    };
    loadVideos();
  }, []);

  const handleVideoClick = (video: VideoType) => {
    setCurrentVideo(video);
  };

  const handleBack = () => {
    Taro.navigateBack();
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

  return (
    <View className={styles.page}>
      {/* 顶部导航 */}
      <View className={styles.navBar}>
        <Text className={styles.navBack} onClick={handleBack}>← 返回</Text>
        <Text className={styles.navTitle}>视频播放</Text>
        <View className={styles.navRight} />
      </View>

      {/* 视频播放器 */}
      <View className={styles.playerWrapper}>
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
      </View>

      {/* 当前视频信息 */}
      <View className={styles.videoInfo}>
        <Text className={styles.videoTitle}>{currentVideo.title}</Text>
        <Text className={styles.videoDesc}>{currentVideo.description}</Text>
        <Text className={styles.videoDuration}>{formatDuration(currentVideo.duration)}</Text>
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