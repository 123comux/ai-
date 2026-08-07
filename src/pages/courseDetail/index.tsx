import React, { useEffect, useState, useRef } from 'react';
import { View, Text, ScrollView, Image } from '@tarojs/components';
import Taro, { useDidShow } from '@tarojs/taro';
import ProgressBar from '@/components/ProgressBar';
import { fetchCourseDetail, fetchCourseVideos, completeLearningPathNode } from '@/services/api';
import { formatDuration, formatMinutes } from '@/utils/index';
import type { Chapter, Video } from '@/types/index';
import styles from './index.module.scss';

const CourseDetailPage: React.FC = () => {
  const [course, setCourse] = useState<any>(null);
  const [videos, setVideos] = useState<Video[]>([]);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [expandedChapters, setExpandedChapters] = useState<Set<string>>(new Set());
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);
  const [completed, setCompleted] = useState(false);
  const pathIdRef = useRef('');
  const nodeIdRef = useRef('');
  const courseIdRef = useRef('');

  const loadCourse = async (initial = false) => {
    try {
      const { id, pathId, nodeId } = Taro.getCurrentInstance().router?.params || {};
      if (!id) { setLoading(false); return; }

      if (pathId) pathIdRef.current = pathId;
      if (nodeId) nodeIdRef.current = nodeId;
      if (id) courseIdRef.current = id;

      if (initial) {
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
      }
      // 每次显示都刷新视频（含看完状态），让学习进度实时更新
      const courseVideos = await fetchCourseVideos(id);
      setVideos(courseVideos);
    } catch (err) {
      console.error('[CourseDetail] load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCourse(true);
  }, []);

  // 从视频页标记"已看完"后返回，刷新学习进度
  useDidShow(() => {
    if (courseIdRef.current) loadCourse(false);
  });

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

  const handleComplete = async () => {
    const pathId = pathIdRef.current;
    const nodeId = nodeIdRef.current;
    if (!pathId || !nodeId || completing || completed) return;
    setCompleting(true);
    try {
      await completeLearningPathNode(pathId, nodeId);
      setCompleted(true);
      Taro.showToast({ title: '已完成，下一个已解锁', icon: 'success' });
    } catch (err: any) {
      console.error('[CourseDetail] complete failed:', err);
      const msg = err?.message || '标记失败，请重试';
      // 后端 400 返回如"还有 n/m 个视频未看完"
      Taro.showToast({ title: msg.slice(0, 40), icon: 'none' });
    } finally {
      setCompleting(false);
    }
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

  /** 打开章节下的某个子视频（分P） */
  const handleChapterSubVideo = (chapterId: string, video: any) => {
    const courseId = course?.id || '';
    Taro.navigateTo({
      url: `/pages/video/index?videoId=${encodeURIComponent(video.id)}&courseId=${encodeURIComponent(courseId)}&chapterId=${encodeURIComponent(chapterId)}`,
    });
  };

  /** 该章节的子视频列表（按 chapter 字段过滤） */
  const chapterVideos = (chapterId: string) => videos.filter((v) => v.chapter === chapterId);

  const handleChapterDetail = (chapter: Chapter) => {
    const courseId = course?.id || '';
    Taro.navigateTo({
      url: `/pages/chapterDetail/index?courseId=${encodeURIComponent(courseId)}&chapterId=${encodeURIComponent(chapter.id)}`,
    });
  };

  if (loading) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  // 学习进度实时计算：已看完视频数 / 该课程总视频数
  const progressPercent = videos.length
    ? Math.round((videos.filter((v) => v.completed).length / videos.length) * 100)
    : 0;

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
          <Text className={styles.metaText}>{formatMinutes(course.duration || (course.estimated_hours || 0) * 60)}</Text>
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
            <Text className={styles.progressValue}>{progressPercent}%</Text>
          </View>
          <ProgressBar percent={progressPercent} height={8} />
          {pathIdRef.current && nodeIdRef.current && (
            <View
              className={`${styles.completeBtn} ${completed ? styles.completeBtnDone : ''}`}
              onClick={handleComplete}
            >
              <Text className={styles.completeBtnText}>
                {completed ? '✓ 已完成' : completing ? '标记中...' : '标记完成'}
              </Text>
            </View>
          )}
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
                  <View className={styles.chapterActions}>
                    <View className={styles.chapterDetailBtn} onClick={(e) => { e.stopPropagation(); handleChapterDetail(ch); }}>
                      <Text className={styles.chapterDetailText}>详情</Text>
                    </View>
                    {ch.video_bv && (
                      <View className={styles.chapterVideoBtn} onClick={(e) => { e.stopPropagation(); handleChapterVideo(ch); }}>
                        <Text className={styles.chapterVideoIcon}>▶</Text>
                      </View>
                    )}
                  </View>
                </View>

                {isExpanded && ch.summary && (
                  <View className={styles.chapterSummary}>
                    <Text className={styles.chapterSummaryText}>{ch.summary}</Text>
                  </View>
                )}

                {/* 本章节子视频（分P精选） */}
                {isExpanded && chapterVideos(ch.id).length > 0 && (
                  <View className={styles.chapterVideos}>
                    {chapterVideos(ch.id).map((video) => (
                      <View
                        key={video.id}
                        className={styles.chapterVideoItem}
                        onClick={() => handleChapterSubVideo(ch.id, video)}
                      >
                        <Text className={styles.chapterVideoItemIcon}>
                          {video.completed ? '✅' : '▶'}
                        </Text>
                        <View className={styles.chapterVideoItemInfo}>
                          <Text className={styles.chapterVideoItemTitle} numberOfLines={1}>
                            {video.title}
                          </Text>
                          <Text className={styles.chapterVideoItemMeta}>
                            {formatDuration(video.duration)}
                            {video.completed ? ' · 已看完' : ''}
                          </Text>
                        </View>
                      </View>
                    ))}
                    {/* 完整版合集标注 + B站链接 */}
                    {ch.video_bv && (
                      <View className={styles.chapterVideoNotice}>
                        <Text className={styles.chapterVideoNoticeText}>
                          本视频为完整版合集，可在 B 站查看全部内容
                        </Text>
                        <Text
                          className={styles.chapterVideoBiliLink}
                          onClick={(e) => {
                            e.stopPropagation();
                            Taro.setClipboardData({
                              data: `https://www.bilibili.com/video/${ch.video_bv}`,
                              success: () => Taro.showToast({ title: '链接已复制，去 B 站查看', icon: 'none' }),
                            });
                          }}
                        >
                          复制 B 站完整版链接 →
                        </Text>
                      </View>
                    )}
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

        {/* 相关视频（精选前 6 个，完整列表见上方各章节） */}
        {videos.length > 0 && (
          <>
            <Text className={styles.sectionTitle}>相关视频</Text>
            <View className={styles.videoList}>
              {videos.slice(0, 6).map((video) => (
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