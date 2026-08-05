import React, { useEffect, useState, useRef } from 'react';
import { View, Text, ScrollView, Swiper, SwiperItem, Image, Input, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import AssessmentCard from '@/components/AssessmentCard';
import PathCard from '@/components/PathCard';
import CourseCard from '@/components/CourseCard';
import ProjectCard from '@/components/ProjectCard';
import { useLearningStore } from '@/store/useLearningStore';
import { useUserStore } from '@/store/useUserStore';
import { fetchAbilityReport, fetchLearningPath, fetchCourses, fetchProjects, askTutor } from '@/services/api';
import { mockDirections } from '@/data/assessment';
import { formatDuration } from '@/utils/index';
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

  // AI 导师对话状态
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'ai'; content: string }[]>([
    { role: 'ai', content: '你好！我是你的 AI 学习导师，有什么问题可以问我～' },
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatScrollRef = useRef<ScrollView>(null);

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

  const handleSendMessage = async () => {
    const text = chatInput.trim();
    if (!text || chatLoading) return;
    setChatInput('');
    setChatMessages((prev) => [...prev, { role: 'user', content: text }]);
    setChatLoading(true);
    try {
      const res = await askTutor(text);
      setChatMessages((prev) => [...prev, { role: 'ai', content: res.answer }]);
    } catch {
      setChatMessages((prev) => [...prev, { role: 'ai', content: '抱歉，我暂时无法回答，请稍后再试。' }]);
    } finally {
      setChatLoading(false);
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
          <View className={styles.aiToolCard} style="background:linear-gradient(135deg,#7c3aed,#a78bfa)" onClick={() => setChatOpen(true)}>
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
          {mockDirections.map((dir) => (
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

      {/* AI 导师对话弹窗 */}
      {chatOpen && (
        <View className={styles.chatOverlay}>
          <View className={styles.chatContainer}>
            <View className={styles.chatHeader}>
              <Text className={styles.chatHeaderTitle}>AI 学习导师</Text>
              <Text className={styles.chatClose} onClick={() => setChatOpen(false)}>关闭</Text>
            </View>
            <ScrollView className={styles.chatMessages} scrollY ref={chatScrollRef}>
              {chatMessages.map((msg, i) => (
                <View key={i} className={`${styles.chatMsg} ${msg.role === 'user' ? styles.chatMsgUser : styles.chatMsgAi}`}>
                  <View className={msg.role === 'user' ? styles.chatBubbleUser : styles.chatBubbleAi}>
                    <Text className={styles.chatText}>{msg.content}</Text>
                  </View>
                </View>
              ))}
              {chatLoading && (
                <View className={styles.chatMsgAi}>
                  <View className={styles.chatBubbleAi}>
                    <Text className={styles.chatText}>正在思考...</Text>
                  </View>
                </View>
              )}
            </ScrollView>
            <View className={styles.chatInputBar}>
              <Input
                className={styles.chatInput}
                placeholder="输入你的问题..."
                value={chatInput}
                onInput={(e) => setChatInput(e.detail.value)}
                onConfirm={handleSendMessage}
                disabled={chatLoading}
                confirmType="send"
              />
              <Button className={styles.chatSendBtn} onClick={handleSendMessage} disabled={chatLoading}>
                发送
              </Button>
            </View>
          </View>
        </View>
      )}
    </ScrollView>
  );
};

export default HomePage;