import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { fetchCourseDetail } from '@/services/api';
import type { Chapter, Section } from '@/types/index';
import styles from './index.module.scss';

/** 对可能 URL 编码的字符串做安全解码 */
const safeDecode = (s: string): string => {
  if (!s) return '';
  try {
    return /%[0-9A-Fa-f]{2}/.test(s) ? decodeURIComponent(s) : s;
  } catch {
    return s;
  }
};

const ChapterDetailPage: React.FC = () => {
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [course, setCourse] = useState<any>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const params = Taro.getCurrentInstance().router?.params || {};
        const { courseId, chapterId } = params as { courseId?: string; chapterId?: string };
        if (!courseId || !chapterId) {
          setLoading(false);
          return;
        }
        const data = await fetchCourseDetail(courseId);
        if (data) {
          setCourse(data);
          const list: Chapter[] = data.chapters || [];
          setChapters(list);
          const target = list.find((ch) => ch.id === chapterId) || null;
          setChapter(target);
          if (target) {
            setExpandedSections(new Set(target.sections?.slice(0, 1).map((s: Section) => s.id) || []));
          }
        }
      } catch (err) {
        console.error('[ChapterDetail] load error:', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const toggleSection = (sectionId: string) => {
    const next = new Set(expandedSections);
    next.has(sectionId) ? next.delete(sectionId) : next.add(sectionId);
    setExpandedSections(next);
  };

  const handlePlayVideo = () => {
    if (!chapter?.video_bv) return;
    const bvUrl = `https://player.bilibili.com/player.html?bvid=${chapter.video_bv}&page=${chapter.video_page || 1}`;
    const courseId = course?.id || '';
    Taro.navigateTo({
      url: `/pages/video/index?videoUrl=${encodeURIComponent(bvUrl)}&videoTitle=${encodeURIComponent(chapter.title)}&courseId=${encodeURIComponent(courseId)}&chapterId=${encodeURIComponent(chapter.id)}`,
    });
  };

  const goChapter = (ch: Chapter | null) => {
    if (!ch) return;
    setChapter(ch);
    setExpandedSections(new Set(ch.sections?.slice(0, 1).map((s: Section) => s.id) || []));
    Taro.pageScrollTo({ scrollTop: 0, duration: 0 });
  };

  if (loading) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  if (!chapter) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>章节不存在</Text>
      </View>
    );
  }

  const idx = chapters.findIndex((ch) => ch.id === chapter.id);
  const prev = idx > 0 ? chapters[idx - 1] : null;
  const next = idx >= 0 && idx < chapters.length - 1 ? chapters[idx + 1] : null;

  return (
    <ScrollView className={styles.page} scrollY>
      {/* 顶部导航 */}
      <View className={styles.navBar}>
        <Text className={styles.navBack} onClick={() => Taro.navigateBack()}>← 返回</Text>
        <Text className={styles.navTitle}>{safeDecode(course?.title || '')}</Text>
        <View className={styles.navRight} />
      </View>

      {/* 章节头部 */}
      <View className={styles.header}>
        <Text className={styles.chapterIndex}>第 {idx + 1} 章</Text>
        <Text className={styles.chapterTitle}>{safeDecode(chapter.title)}</Text>
        <Text className={styles.chapterSummary}>{safeDecode(chapter.summary)}</Text>
        <View className={styles.chapterMeta}>
          <Text className={styles.metaText}>{chapter.duration_minutes} 分钟</Text>
          <Text className={styles.metaDot}>·</Text>
          <Text className={styles.metaText}>{chapter.sections?.length || 0} 个小节</Text>
        </View>

        {chapter.video_bv && (
          <View className={styles.playBtn} onClick={handlePlayVideo}>
            <View className={styles.playIconWrap}>
              <Text className={styles.playIcon}>▶</Text>
            </View>
            <View className={styles.playBtnText}>
              <Text className={styles.playBtnTitle}>观看本章视频</Text>
              <Text className={styles.playBtnDesc}>B站视频 · 支持全屏</Text>
            </View>
          </View>
        )}
      </View>

      {/* 小节列表 */}
      <Text className={styles.sectionListTitle}>本章小节</Text>
      <View className={styles.sectionList}>
        {chapter.sections?.length > 0 ? chapter.sections.map((sec, i) => {
          const isExpanded = expandedSections.has(sec.id);
          return (
            <View key={sec.id} className={styles.sectionItem}>
              <View className={styles.sectionHeader} onClick={() => toggleSection(sec.id)}>
                <View className={styles.sectionIndex}>
                  <Text className={styles.sectionIndexText}>{i + 1}</Text>
                </View>
                <Text className={styles.sectionTitleText}>{safeDecode(sec.title)}</Text>
                <Text className={styles.sectionArrow}>{isExpanded ? '▾' : '▸'}</Text>
              </View>

              {isExpanded && (
                <View className={styles.sectionContent}>
                  {sec.content && (
                    <Text className={styles.sectionDesc}>{safeDecode(sec.content)}</Text>
                  )}

                  {sec.knowledge_points?.length > 0 && (
                    <View className={styles.knowledgeBlock}>
                      <Text className={styles.knowledgeLabel}>📌 核心知识点</Text>
                      {sec.knowledge_points.map((kp: string, kIdx: number) => (
                        <View key={kIdx} className={styles.knowledgeItem}>
                          <Text className={styles.knowledgeBullet}>•</Text>
                          <Text className={styles.knowledgeText}>{safeDecode(kp)}</Text>
                        </View>
                      ))}
                    </View>
                  )}

                  {sec.case && (
                    <View className={styles.caseBlock}>
                      <Text className={styles.caseLabel}>💡 实战案例</Text>
                      <Text className={styles.caseText}>{safeDecode(sec.case)}</Text>
                    </View>
                  )}
                </View>
              )}
            </View>
          );
        }) : (
          <Text className={styles.emptyText}>暂无小节内容</Text>
        )}
      </View>

      {/* 上一章 / 下一章 */}
      {(prev || next) && (
        <View className={styles.chapterNav}>
          <View
            className={`${styles.navItem} ${prev ? styles.navItemActive : ''}`}
            onClick={() => prev && goChapter(prev)}
          >
            <Text className={styles.navItemLabel}>上一章</Text>
            <Text className={`${styles.navItemTitle} ${prev ? '' : styles.navItemDisabled}`}>
              {prev ? safeDecode(prev.title) : '已是第一章'}
            </Text>
          </View>
          <View
            className={`${styles.navItem} ${next ? styles.navItemActive : ''}`}
            onClick={() => next && goChapter(next)}
          >
            <Text className={styles.navItemLabel}>下一章</Text>
            <Text className={`${styles.navItemTitle} ${next ? '' : styles.navItemDisabled}`}>
              {next ? safeDecode(next.title) : '已是最后一章'}
            </Text>
          </View>
        </View>
      )}
    </ScrollView>
  );
};

export default ChapterDetailPage;
