import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Image } from '@tarojs/components';
import Taro from '@tarojs/taro';
import ProgressBar from '@/components/ProgressBar';
import { fetchCourseDetail, fetchCourseVideos } from '@/services/api';
import { formatDuration } from '@/utils/index';
import type { Video } from '@/types/index';
import styles from './index.module.scss';

interface Section {
  id: string;
  title: string;
  content: string;
  knowledge_points: string[];
  case: string;
}

interface Chapter {
  id: string;
  title: string;
  duration_minutes: number;
  summary: string;
  video_bv: string;
  video_page: number;
  sections: Section[];
}

const CourseDetailPage: React.FC = () => {
  const [course, setCourse] = useState<any>(null);
  const [videos, setVideos] = useState<Video[]>([]);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [expandedChapters, setExpandedChapters] = useState<Set<string>>(new Set());
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCourse = async () => {
      try {
        const { id } = Taro.getCurrentInstance().router?.params || {};
        if (!id) { setLoading(false); return; }

        const data = await fetchCourseDetail(id);
        if (data) {
          setCourse(data);
          if (data.chapters) {
            setChapters(data.chapters);
            if (data.chapters.length > 0) {
              setExpandedChapters(new Set([data.chapters[0].id]));
            }
          }
        }
        const courseVideos = await fetchCourseVideos(id);
        setVideos(courseVideos);
      } catch (err) {
        console.error('[CourseDetail] load error:', err);
      } finally {
        setLoading(false);
      }
    };
    loadCourse();
  }, []);

  const toggleChapter = (chapterId: string) => {
    const next = new Set(expandedChapters);
    next.has(chapterId) ? next.delete(chapterId) : next.add(chapterId);
    setExpandedChapters(next);
  };

  const toggleSection = (sectionId: string) => {
    const next = new Set(expandedSections);
    next.has(sectionId) ? next.delete(sectionId) : next.add(sectionId);
    setExpandedSections(next);
  };

  const handleVideoClick = (video: Video) => {
    Taro.navigateTo({ url: `/pages/video/index?videoId=${video.id}` });
  };

  const handleChapterVideo = (chapter: Chapter) => {
    if (chapter.video_bv) {
      const bvUrl = `https://player.bilibili.com/player.html?bvid=${chapter.video_bv}&page=${chapter.video_page || 1}`;
      const courseId = course?.id || '';
      Taro.navigateTo({
        url: `/pages/video/index?videoUrl=${encodeURIComponent(bvUrl)}&videoTitle=${encodeURIComponent(chapter.title)}&courseId=${encodeURIComponent(courseId)}&chapterId=${encodeURIComponent(chapter.id)}`,
      });
    }
  };

  if (loading) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  if (!course) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>课程不存在</Text>
      </View>
    );
  }

  return (
    <ScrollView className={styles.page} scrollY>
      <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
        <Text className={styles.navBack}>← 返回</Text>
      </View>
      <Image className={styles.cover} src={course.coverImg || course.cover_img || ''} mode="aspectFill" />
      <View className={styles.body}>
        <Text className={styles.title}>{course.title}</Text>
        <Text className={styles.desc}>{course.description}</Text>
        <View className={styles.meta}>
          <Text className={styles.metaText}>{course.lessons} 节课程</Text>
          <Text className={styles.metaDot}>·</Text>
          <Text className={styles.metaText}>{formatDuration(course.duration || (course.estimated_hours || 0) * 60)}</Text>
          {!course.isFree && (
            <>
              <Text className={styles.metaDot}>·</Text>
              <Text className={styles.proText}>PRO 课程</Text>
            </>
          )}
        </View>
        <View className={styles.progressSection}>
          <View className={styles.progressHeader}>
            <Text className={styles.progressLabel}>学习进度</Text>
            <Text className={styles.progressValue}>{course.progress || 0}%</Text>
          </View>
          <ProgressBar percent={course.progress || 0} height={8} />
        </View>

        {/* 课程目录 - 富文本 */}
        <Text className={styles.sectionTitle}>课程目录</Text>
        <View className={styles.chapterList}>
          {chapters.length > 0 ? chapters.map((ch) => {
            const isExpanded = expandedChapters.has(ch.id);
            return (
              <View key={ch.id} className={styles.chapterItem}>
                <View className={styles.chapterHeader} onClick={() => toggleChapter(ch.id)}>
                  <View className={styles.chapterStatus}>
                    <Text className={styles.statusIcon}>{isExpanded ? '▼' : '▶'}</Text>
                  </View>
                  <View className={styles.chapterInfo}>
                    <Text className={styles.chapterTitle}>{ch.title}</Text>
                    <Text className={styles.chapterDuration}>{ch.duration_minutes} 分钟 · {ch.sections?.length || 0} 小节</Text>
                  </View>
                  {ch.video_bv && (
                    <View className={styles.chapterVideoBtn} onClick={(e) => { e.stopPropagation(); handleChapterVideo(ch); }}>
                      <Text className={styles.chapterVideoIcon}>▶</Text>
                    </View>
                  )}
                </View>

                {isExpanded && ch.summary && (
                  <View className={styles.chapterSummary}>
                    <Text className={styles.chapterSummaryText}>{ch.summary}</Text>
                  </View>
                )}

                {isExpanded && ch.sections?.map((sec) => {
                  const secExpanded = expandedSections.has(sec.id);
                  return (
                    <View key={sec.id} className={styles.sectionItem}>
                      <View className={styles.sectionHeader} onClick={() => toggleSection(sec.id)}>
                        <Text className={styles.sectionArrow}>{secExpanded ? '▾' : '▸'}</Text>
                        <Text className={styles.sectionTitle}>{sec.title}</Text>
                      </View>

                      {secExpanded && (
                        <View className={styles.sectionContent}>
                          <Text className={styles.sectionDesc}>{sec.content}</Text>

                          {sec.knowledge_points?.length > 0 && (
                            <View className={styles.knowledgeBlock}>
                              <Text className={styles.knowledgeLabel}>📌 核心知识点</Text>
                              {sec.knowledge_points.map((kp: string, idx: number) => (
                                <View key={idx} className={styles.knowledgeItem}>
                                  <Text className={styles.knowledgeBullet}>•</Text>
                                  <Text className={styles.knowledgeText}>{kp}</Text>
                                </View>
                              ))}
                            </View>
                          )}

                          {sec.case && (
                            <View className={styles.caseBlock}>
                              <Text className={styles.caseLabel}>💡 实战案例</Text>
                              <Text className={styles.caseText}>{sec.case}</Text>
                            </View>
                          )}
                        </View>
                      )}
                    </View>
                  );
                })}
              </View>
            );
          }) : (
            <Text className={styles.chapterTitle}>暂无章节信息</Text>
          )}
        </View>

        {/* 相关视频 */}
        {videos.length > 0 && (
          <>
            <Text className={styles.sectionTitle}>相关视频</Text>
            <View className={styles.videoList}>
              {videos.map((video) => (
                <View
                  key={video.id}
                  className={styles.videoItem}
                  onClick={() => handleVideoClick(video)}
                >
                  <Image className={styles.videoCover} src={video.coverUrl} mode="aspectFill" />
                  <View className={styles.videoItemInfo}>
                    <Text className={styles.videoItemTitle}>{video.title}</Text>
                    <Text className={styles.videoItemDuration}>{formatDuration(video.duration)}</Text>
                  </View>
                  <Text className={styles.videoItemArrow}>▶</Text>
                </View>
              ))}
            </View>
          </>
        )}
      </View>
    </ScrollView>
  );
};

export default CourseDetailPage;