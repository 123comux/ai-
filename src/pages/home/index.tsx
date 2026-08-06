import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Swiper, SwiperItem, Image } from '@tarojs/components';
import Taro from '@tarojs/taro';
import AssessmentCard from '@/components/AssessmentCard';
import PathCard from '@/components/PathCard';
import CourseCard from '@/components/CourseCard';
import ProjectCard from '@/components/ProjectCard';
import { useLearningStore } from '@/store/useLearningStore';
import { useUserStore } from '@/store/useUserStore';
import { fetchAbilityReport, fetchLearningPath, fetchCourses, fetchProjects } from '@/services/api';
import type { Course, Project } from '@/types/index';
import styles from './index.module.scss';

const HomePage: React.FC = () => {
  const { nickname, targetDirection } = useUserStore();
  const {
    abilityReport, setAbilityReport,
    currentPath, setCurrentPath,
    setCourses, setProjects,
    learningDays, totalHours, completedProjects,
  } = useLearningStore();

  const [courses, setLocalCourses] = useState<Course[]>([]);
  const [projects, setLocalProjects] = useState<Project[]>([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [report, path, courseData, projectData] = await Promise.all([
          fetchAbilityReport(),
          fetchLearningPath(),
          fetchCourses(),
          fetchProjects(),
        ]);
        setAbilityReport(report);
        setCurrentPath(path);
        setLocalCourses(courseData.slice(0, 4));
        setLocalProjects(projectData.slice(0, 4));
        setCourses(courseData);
        setProjects(projectData);
      } catch (err) {
        console.error('[Home] load data error:', err);
      }
    };
    loadData();
  }, []);

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

  const bannerList = [
    { id: 1, img: 'https://picsum.photos/id/160/750/400', title: 'AI 能力测评', desc: '测测你的 AI 水平' },
    { id: 2, img: 'https://picsum.photos/id/201/750/400', title: '实战项目', desc: '做出可写进简历的作品' },
    { id: 3, img: 'https://picsum.photos/id/119/750/400', title: '岗位对标', desc: '看看你离目标岗位差多少' },
  ];

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
      <View className={styles.bannerWrap}>
        <Swiper
          className={styles.banner}
          indicatorColor="#e5e6eb"
          indicatorActiveColor="#165dff"
          circular
          autoplay
          interval={3000}
        >
          {bannerList.map((item) => (
            <SwiperItem key={item.id}>
              <View className={styles.bannerSlide}>
                <Image className={styles.bannerImg} src={item.img} mode="aspectFill" />
                <View className={styles.bannerOverlay}>
                  <Text className={styles.bannerTitle}>{item.title}</Text>
                  <Text className={styles.bannerDesc}>{item.desc}</Text>
                </View>
              </View>
            </SwiperItem>
          ))}
        </Swiper>
      </View>

      {/* 学习统计 */}
      <View className={styles.statsRow}>
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{learningDays}</Text>
          <Text className={styles.statLabel}>学习天数</Text>
        </View>
        <View className={styles.statDivider} />
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{totalHours}</Text>
          <Text className={styles.statLabel}>学习时长(h)</Text>
        </View>
        <View className={styles.statDivider} />
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{completedProjects}</Text>
          <Text className={styles.statLabel}>完成项目</Text>
        </View>
      </View>

      {/* AI 智能工具 */}
      <View className={styles.section}>
        <View className={styles.sectionHeader}>
          <Text className={styles.sectionTitle}>AI 智能工具</Text>
        </View>
        <View className={styles.aiTools}>
          <View className={styles.aiToolCard} style="background:linear-gradient(135deg,#7c3aed,#a78bfa)" onClick={() => Taro.navigateTo({ url: '/pages/tutor/index' })}>
            <Text className={styles.aiToolIcon}>💬</Text>
            <Text className={styles.aiToolName}>AI 导师</Text>
            <Text className={styles.aiToolDesc}>问答学习</Text>
          </View>
          <View className={styles.aiToolCard} style="background:linear-gradient(135deg,#165dff,#4080ff)" onClick={handleStartAssessment}>
            <Text className={styles.aiToolIcon}>🧠</Text>
            <Text className={styles.aiToolName}>能力分析</Text>
            <Text className={styles.aiToolDesc}>AI 精准评估</Text>
          </View>
          <View className={styles.aiToolCard} style="background:linear-gradient(135deg,#00b42a,#27c346)" onClick={() => Taro.switchTab({ url: '/pages/learn/index' })}>
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

      {/* 学习方向 */}
      <View className={styles.section}>
        <View className={styles.sectionHeader}>
          <Text className={styles.sectionTitle}>学习方向</Text>
        </View>
        <ScrollView className={styles.directionScroll} scrollX>
          {[
            { id: '1', name: 'AI 算法工程师', description: '机器学习、深度学习、大模型微调', color: '#165dff' },
            { id: '2', name: 'AI 产品经理', description: 'AI 产品设计、Prompt Engineering', color: '#7c3aed' },
            { id: '3', name: 'AIGC 应用人才', description: 'AI 绘画、AI 写作、AI 视频', color: '#00b42a' },
            { id: '4', name: '数据分析工程师', description: 'Python 数据分析、SQL、BI', color: '#ff7d00' },
            { id: '5', name: 'AI 应用开发', description: '大模型 API、RAG、Agent', color: '#f53f3f' },
          ].map((dir) => (
            <View
              key={dir.id}
              className={styles.directionCard}
              style={{ borderTopColor: dir.color }}
              onClick={() => {
                Taro.navigateTo({ url: '/pages/learningPath/index' });
              }}
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