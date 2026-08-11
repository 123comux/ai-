import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Swiper, SwiperItem, Image } from '@tarojs/components';
import Taro, { useDidShow } from '@tarojs/taro';
import AssessmentCard from '@/components/AssessmentCard';
import PathCard from '@/components/PathCard';
import CourseCard from '@/components/CourseCard';
import ProjectCard from '@/components/ProjectCard';
import { useLearningStore } from '@/store/useLearningStore';
import { useUserStore } from '@/store/useUserStore';
import { fetchAbilityReport, fetchLearningPath, fetchCourses, fetchProjects, getRecommendedCourses, fetchBanners, fetchDirections, fetchLearningStats } from '@/services/api';
import type { Course, Project } from '@/types/index';
import type { CourseRecommendation, BannerItem, DirectionItem } from '@/services/api';
import styles from './index.module.scss';

/** 学习方向 → 课程阶段映射（用于过滤课程） */
const DIRECTION_TOPIC_MAP: Record<string, string> = {
  '零基础认知': '认知',
  '入门实践': '入门',
  '提示词进阶': '进阶',
  '场景实战': '实战',
  '熟练精通': '熟练',
  // 兼容测评推荐方向（assessment_service 返回的方向名）
  '零基础入门': '入门',
  'AI办公提效': '实战',
  'AI项目实战': '熟练',
  '系统掌握AI': '进阶',
};

/** 课程阶段 / 难度 → 中文展示 */
const TOPIC_CN_MAP: Record<string, string> = {
  '认知': '认知',
  '入门': '入门',
  '进阶': '进阶',
  '实战': '实战',
  '熟练': '熟练',
  'beginner': '入门',
  'intermediate': '进阶',
  'advanced': '高级',
};

const HomePage: React.FC = () => {
  const { nickname, targetDirection } = useUserStore();
  const {
    abilityReport, setAbilityReport,
    currentPath, setCurrentPath,
    setCourses, setProjects, setSelectedTopic,
  } = useLearningStore();

  const [stats, setStats] = useState<{ learningDays: number; totalMinutes: number; completedProjects: number }>({ learningDays: 0, totalMinutes: 0, completedProjects: 0 });

  const [courses, setLocalCourses] = useState<Course[]>([]);
  const [projects, setLocalProjects] = useState<Project[]>([]);
  const [aiRecommendations, setAiRecommendations] = useState<CourseRecommendation[]>([]);
  const [banners, setBanners] = useState<BannerItem[]>([]);
  const [directions, setDirections] = useState<DirectionItem[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  // 每次页面显示时刷新（从学习路径/课程页标记完成后返回，路径进度同步更新）
  useDidShow(() => {
    loadData();
  });

  const loadData = async () => {
    try {
      const [report, path, courseData, projectData, bannerData, directionData, statsData] = await Promise.all([
        fetchAbilityReport(),
        fetchLearningPath(),
        fetchCourses(),
        fetchProjects(),
        fetchBanners(),
        fetchDirections(),
        fetchLearningStats(),
      ]);
      setStats(statsData);
      setAbilityReport(report);
      setCurrentPath(path);
      setLocalCourses(courseData.slice(0, 4));
      setLocalProjects(projectData.slice(0, 4));
      setCourses(courseData);
      setProjects(projectData);
      setBanners(bannerData);
      setDirections(directionData);

      // 根据用户目标方向获取 AI 推荐课程
      if (targetDirection && DIRECTION_TOPIC_MAP[targetDirection]) {
        try {
          const recs = await getRecommendedCourses(DIRECTION_TOPIC_MAP[targetDirection], 4);
          setAiRecommendations(recs);
        } catch {
          // 推荐接口不可用时忽略
        }
      }
    } catch (err) {
      console.error('[Home] load data error:', err);
    }
  };

  const handleStartAssessment = () => {
    Taro.navigateTo({ url: '/pages/assessment/index' });
  };

  const handleViewPath = () => {
    Taro.navigateTo({ url: '/pages/learningPath/index' });
  };

  const handleViewCourse = (id: string) => {
    Taro.navigateTo({ url: `/pages/courseDetail/index?id=${id}` });
  };

  const handleViewProject = (id: string) => {
    Taro.navigateTo({ url: `/pages/projectDetail/index?id=${id}` });
  };

  const handleViewAll = (type: 'course' | 'project') => {
    Taro.switchTab({ url: type === 'course' ? '/pages/learn/index' : '/pages/project/index' });
  };

  /** 选择学习方向 → 设置话题并跳转到学习页 */
  const handleSelectDirection = (directionName: string) => {
    const topic = DIRECTION_TOPIC_MAP[directionName] || 'all';
    setSelectedTopic(topic);
    Taro.switchTab({ url: '/pages/learn/index' });
  };

  /** AI 课程推荐 → 跳转到学习页展示推荐 */
  const handleCourseRecommend = () => {
    // 如果有测评结果，使用推荐方向；否则使用用户目标方向
    const interest = abilityReport?.recommendedDirection || targetDirection;
    const topic = DIRECTION_TOPIC_MAP[interest] || 'all';
    setSelectedTopic(topic);
    Taro.switchTab({ url: '/pages/learn/index' });
  };

  return (
    <ScrollView className={styles.page} scrollY>
      {/* 顶部用户信息 */}
      <View className={styles.header}>
        <View className={styles.headerTop}>
          <View className={styles.userInfo}>
            <Image className={styles.avatar} src="https://picsum.photos/id/64/200/200" mode="aspectFill" />
            <View className={styles.userText}>
              <Text className={styles.greeting}>你好，{nickname}</Text>
              <Text className={styles.direction}>目标：{targetDirection}</Text>
            </View>
          </View>
          <View className={styles.notification}>
            <Text className={styles.notificationIcon}>🔔</Text>
          </View>
        </View>
      </View>

      {/* Banner 轮播 */}
      {banners.length > 0 && (
        <View className={styles.bannerWrap}>
          <Swiper
            className={styles.banner}
            indicatorColor="#e5e6eb"
            indicatorActiveColor="#165dff"
            circular
            autoplay
            interval={3000}
          >
            {banners.map((item) => (
              <SwiperItem key={item.id}>
                <View className={styles.bannerSlide}>
                  <Image className={styles.bannerImg} src={item.image_url} mode="aspectFill" />
                  <View className={styles.bannerOverlay}>
                    <Text className={styles.bannerTitle}>{item.title}</Text>
                    <Text className={styles.bannerDesc}>{item.description}</Text>
                  </View>
                </View>
              </SwiperItem>
            ))}
          </Swiper>
        </View>
      )}

      {/* 学习统计 */}
      <View className={styles.statsRow}>
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{stats.learningDays}</Text>
          <Text className={styles.statLabel}>学习天数</Text>
        </View>
        <View className={styles.statDivider} />
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{stats.totalMinutes}</Text>
          <Text className={styles.statLabel}>学习时长(min)</Text>
        </View>
        <View className={styles.statDivider} />
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{stats.completedProjects}</Text>
          <Text className={styles.statLabel}>完成项目</Text>
        </View>
      </View>

      {/* AI 智能工具 */}
      <View className={styles.section}>
        <View className={styles.sectionHeader}>
          <Text className={styles.sectionTitle}>AI 智能工具</Text>
        </View>
        <View className={styles.aiTools}>
          <View className={styles.aiToolCard} style={{ background: 'linear-gradient(135deg, #7c3aed, #a78bfa)' }} onClick={() => Taro.navigateTo({ url: '/pages/tutor/index' })}>
            <Text className={styles.aiToolIcon}>💬</Text>
            <Text className={styles.aiToolName}>AI 导师</Text>
            <Text className={styles.aiToolDesc}>问答学习</Text>
          </View>
          <View className={styles.aiToolCard} style={{ background: 'linear-gradient(135deg, #165dff, #4080ff)' }} onClick={handleStartAssessment}>
            <Text className={styles.aiToolIcon}>🧠</Text>
            <Text className={styles.aiToolName}>能力分析</Text>
            <Text className={styles.aiToolDesc}>AI 精准评估</Text>
          </View>
          <View className={styles.aiToolCard} style={{ background: 'linear-gradient(135deg, #00b42a, #27c346)' }} onClick={handleCourseRecommend}>
            <Text className={styles.aiToolIcon}>📚</Text>
            <Text className={styles.aiToolName}>课程推荐</Text>
            <Text className={styles.aiToolDesc}>AI 智能匹配</Text>
          </View>
        </View>
      </View>

      {/* 能力测评 */}
      <View className={styles.section}>
        {abilityReport ? (
          <AssessmentCard
            overallScore={abilityReport.overallScore}
            level={abilityReport.level}
            direction={abilityReport.recommendedDirection}
            onClick={handleStartAssessment}
          />
        ) : (
          <View className={styles.assessmentEntry} onClick={handleStartAssessment}>
            <Text className={styles.assessmentEntryIcon}>🧠</Text>
            <View className={styles.assessmentEntryText}>
              <Text className={styles.assessmentEntryTitle}>开始 AI 能力测评</Text>
              <Text className={styles.assessmentEntryDesc}>15 分钟，精准定位你的 AI 水平</Text>
            </View>
            <Text className={styles.arrow}>→</Text>
          </View>
        )}
      </View>

      {/* 学习方向（点击后过滤课程） */}
      <View className={styles.section}>
        <View className={styles.sectionHeader}>
          <Text className={styles.sectionTitle}>学习方向</Text>
          <Text className={styles.sectionMore} onClick={() => Taro.switchTab({ url: '/pages/learn/index' })}>查看课程 →</Text>
        </View>
        <ScrollView className={styles.directionScroll} scrollX>
          {directions.map((dir) => (
            <View
              key={dir.id}
              className={styles.directionCard}
              style={{ borderTopColor: dir.color }}
              onClick={() => handleSelectDirection(dir.name)}
            >
              <Text className={styles.directionName}>{dir.name}</Text>
              <Text className={styles.directionDesc}>{dir.description}</Text>
            </View>
          ))}
        </ScrollView>
      </View>

      {/* 学习路径 */}
      {currentPath && (
        <View className={styles.section}>
          <View className={styles.sectionHeader}>
            <Text className={styles.sectionTitle}>我的学习路径</Text>
            <Text className={styles.sectionMore} onClick={handleViewPath}>查看全部 →</Text>
          </View>
          <PathCard path={currentPath} onClick={handleViewPath} />
        </View>
      )}

      {/* AI 推荐课程（基于用户目标方向） */}
      {aiRecommendations.length > 0 && (
        <View className={styles.section}>
          <View className={styles.sectionHeader}>
            <Text className={styles.sectionTitle}>AI 推荐课程</Text>
            <Text className={styles.sectionMore} onClick={handleCourseRecommend}>更多 →</Text>
          </View>
          <View className={styles.recommendList}>
            {aiRecommendations.map((rec, i) => (
              <View key={i} className={styles.recommendItem} onClick={() => handleViewCourse(rec.id)}>
                <Text className={styles.recommendItemTitle}>{rec.title}</Text>
                <Text className={styles.recommendItemMeta}>
                  {TOPIC_CN_MAP[rec.topic] || rec.topic} · {TOPIC_CN_MAP[rec.difficulty] || rec.difficulty} · 匹配度 {Math.round(rec.score * 100)}%
                </Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* 推荐课程 */}
      <View className={styles.section}>
        <View className={styles.sectionHeader}>
          <Text className={styles.sectionTitle}>推荐课程</Text>
          <Text className={styles.sectionMore} onClick={() => handleViewAll('course')}>更多 →</Text>
        </View>
        <View className={styles.courseGrid}>
          {courses.map((course) => (
            <View key={course.id} className={styles.courseItem}>
              <CourseCard course={course} onClick={() => handleViewCourse(course.id)} />
            </View>
          ))}
        </View>
      </View>

      {/* 推荐项目 */}
      <View className={styles.section}>
        <View className={styles.sectionHeader}>
          <Text className={styles.sectionTitle}>推荐项目</Text>
          <Text className={styles.sectionMore} onClick={() => handleViewAll('project')}>更多 →</Text>
        </View>
        <View className={styles.projectGrid}>
          {projects.map((project) => (
            <View key={project.id} className={styles.projectItem}>
              <ProjectCard project={project} onClick={() => handleViewProject(project.id)} />
            </View>
          ))}
        </View>
      </View>

    </ScrollView>
  );
};

export default HomePage;