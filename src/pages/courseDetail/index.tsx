import React, { useEffect, useState, useRef } from 'react';
import { View, Text, ScrollView, Image, Button } from '@tarojs/components';
import Taro, { useDidShow, useShareAppMessage } from '@tarojs/taro';
import ProgressBar from '@/components/ProgressBar';
import { fetchCourseDetail, fetchCourseVideos, completeLearningPathNode, addFavorite, removeFavorite, fetchFavorites, shareUnlock, fetchShareUnlocks, fetchCourseProgress, completeCourseChapter } from '@/services/api';
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
  const [favorited, setFavorited] = useState(false);
  const [favId, setFavId] = useState(0);
  const pathIdRef = useRef('');
  const nodeIdRef = useRef('');
  const courseIdRef = useRef('');
  const [unlocked, setUnlocked] = useState(false);
  // 章节学习进度：五阶段课程按"已学完章节/总章节"计（不依赖遗留视频库）
  const [chapterDone, setChapterDone] = useState<Set<string>>(new Set());

  // 加载章节完成状态
  const loadChapterProgress = async (courseId: string) => {
    try {
      const p = await fetchCourseProgress(courseId);
      setChapterDone(new Set(p.completed_chapter_ids));
    } catch (e) {
      console.error('[CourseDetail] chapter progress', e);
    }
  };

  // 标记某章节学完（幂等；学完计入课程进度与押金完课率）
  // 后端要求先看完本章配套视频（完课率是押金达标依据，不能空点），未看完时引导直接去播放
  const markChapterDone = async (chapterId: string, chapter?: Chapter) => {
    if (chapterDone.has(chapterId) || !courseIdRef.current) return;
    try {
      await completeCourseChapter(courseIdRef.current, chapterId);
      setChapterDone((prev) => new Set(prev).add(chapterId));
      Taro.showToast({ title: '本章已学完', icon: 'success' });
    } catch (err: any) {
      const msg = err?.message || '标记失败';
      if (msg.includes('视频')) {
        Taro.showModal({
          title: '需要先看完本章视频',
          content: '完课率是押金达标的依据，请先完整观看本章配套视频，再回来标记学完。',
          confirmText: '去看视频',
          cancelText: '稍后',
          success: (res) => {
            if (res.confirm && chapter && chapter.video_bv) handleChapterVideo(chapter);
          },
        });
        return;
      }
      Taro.showToast({ title: msg, icon: 'none' });
    }
  };

  // 分享解锁：右上角菜单转发带课程 id（hook 必须在组件函数体内调用）
  useShareAppMessage(() => ({
    title: course ? `我在学「${course.title}」，一起解锁进阶实操` : '一起学 AI',
    path: `/pages/courseDetail/index?id=${courseIdRef.current}`,
  }));

  const loadUnlockStatus = async () => {
    try {
      const list = await fetchShareUnlocks();
      const found = list.some((u) => u.share_type === 'course' && u.share_target === courseIdRef.current);
      setUnlocked(found);
    } catch (e) {
      console.error('[CourseDetail] unlock status', e);
    }
  };

  const handleShareUnlock = async () => {
    if (!courseIdRef.current || unlocked) return;
    try {
      await shareUnlock('course', courseIdRef.current);
      setUnlocked(true);
      Taro.showToast({ title: '已解锁进阶实操', icon: 'success' });
    } catch (err: any) {
      Taro.showToast({ title: err?.message || '解锁失败', icon: 'none' });
    }
  };

  const checkFavorite = async (courseId: string) => {
    try {
      const favs = await fetchFavorites();
      const found = favs.find((f) => f.item_type === 'course' && f.item_id === courseId);
      if (found) {
        setFavorited(true);
        setFavId(found.id);
      } else {
        setFavorited(false);
        setFavId(0);
      }
    } catch (err) {
      console.error('[CourseDetail] check favorite error:', err);
    }
  };

  const handleFavorite = async () => {
    if (!courseIdRef.current) return;
    try {
      if (favorited) {
        await removeFavorite(favId);
        setFavorited(false);
        setFavId(0);
        Taro.showToast({ title: '已取消收藏', icon: 'none' });
      } else {
        const fav = await addFavorite('course', courseIdRef.current);
        setFavorited(true);
        setFavId(fav.id);
        Taro.showToast({ title: '已收藏', icon: 'success' });
      }
    } catch (err) {
      console.error('[CourseDetail] favorite error:', err);
      Taro.showToast({ title: '操作失败', icon: 'none' });
    }
  };

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
        checkFavorite(id);
        loadUnlockStatus();
        loadChapterProgress(id);
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

  // 仅挂载时加载一次，后续靠 useDidShow 刷新；loadCourse 只用 setState/store
  /* eslint-disable react-hooks/exhaustive-deps */
  useEffect(() => {
    loadCourse(true);
  }, []);
  /* eslint-enable react-hooks/exhaustive-deps */

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

  // 学习进度：五阶段课程按"已学完章节/总章节"计算；无章节课程退化为按视频（兼容旧数据）
  const progressPercent = chapters.length
    ? Math.round((chapterDone.size / chapters.length) * 100)
    : (videos.length ? Math.round((videos.filter((v) => v.completed).length / videos.length) * 100) : 0);

  // 分享解锁后的进阶内容：聚合各章节的实战案例与提示词要点
  const advancedContent: { title: string; content: string }[] = (() => {
    const items: { title: string; content: string }[] = [];
    chapters.forEach((ch) => {
      (ch.sections || []).forEach((sec) => {
        if (sec.case) items.push({ title: `${ch.title} · ${sec.title} · 实战案例`, content: sec.case });
        if (sec.knowledge_points && sec.knowledge_points.length) {
          items.push({ title: `${ch.title} · ${sec.title} · 提示词要点`, content: sec.knowledge_points.join('；') });
        }
      });
    });
    return items;
  })();

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
      <View className={styles.favBtn} onClick={handleFavorite}>
        <Text className={styles.favBtnText}>{favorited ? '⭐' : '☆'}</Text>
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

        {/* 分享解锁进阶实操 */}
        <View className={`${styles.unlockCard} ${unlocked ? styles.unlockCardDone : ''}`}>
          {unlocked ? (
            <>
              <Text className={styles.unlockBadge}>🔓 已解锁进阶实操</Text>
              {advancedContent.length === 0 ? (
                <Text className={styles.unlockEmpty}>本课暂无额外进阶内容</Text>
              ) : advancedContent.map((item, idx) => (
                <View key={idx} className={styles.unlockItem}>
                  <Text className={styles.unlockItemTitle}>{item.title}</Text>
                  <Text className={styles.unlockItemText}>{item.content}</Text>
                </View>
              ))}
            </>
          ) : (
            <>
              <Text className={styles.unlockGuide}>分享给好友，解锁本课进阶实操</Text>
              <View className={styles.unlockActions}>
                {/* open-type=share 无 success 回调（微信分享面板不返回结果），解锁走下方手动兜底 */}
                <Button className={styles.unlockBtn} openType="share">
                  分享解锁
                </Button>
                <Text className={styles.unlockManual} onClick={handleShareUnlock}>我已分享，手动解锁</Text>
              </View>
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
                    <View
                      className={chapterDone.has(ch.id) ? styles.chapterDoneBtn : styles.chapterDoneBtnGhost}
                      onClick={(e) => { e.stopPropagation(); markChapterDone(ch.id, ch); }}
                    >
                      <Text className={chapterDone.has(ch.id) ? styles.chapterDoneText : styles.chapterDoneGhostText}>
                        {chapterDone.has(ch.id) ? '✓ 已学完' : '标记学完'}
                      </Text>
                    </View>
                    <View className={styles.chapterDetailBtn} onClick={(e) => { e.stopPropagation(); handleChapterDetail(ch); }}>
                      <Text className={styles.chapterDetailText}>详情</Text>
                    </View>
                    {ch.video_bv ? (
                      <View className={styles.chapterVideoBtn} onClick={(e) => { e.stopPropagation(); handleChapterVideo(ch); }}>
                        <Text className={styles.chapterVideoIcon}>▶</Text>
                      </View>
                    ) : (
                      <View className={styles.chapterVideoPending}>
                        <Text className={styles.chapterVideoPendingText}>待补充</Text>
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