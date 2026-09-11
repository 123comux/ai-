import React, { useEffect, useRef, useState, Fragment } from 'react';
import { View, Text, ScrollView, Swiper, SwiperItem, Image } from '@tarojs/components';
import Taro, { useDidShow } from '@tarojs/taro';
import AssessmentCard from '@/components/AssessmentCard';
import PathCard from '@/components/PathCard';
import CourseCard from '@/components/CourseCard';
import ProjectCard from '@/components/ProjectCard';
import AccessGate from '@/components/AccessGate';
import { Button, Panel, Stat, SectionHeader, Tag, Reveal } from '@/components/ui';
import { useLearningStore } from '@/store/useLearningStore';
import { useUserStore } from '@/store/useUserStore';
import { useAccessStore, formatTrialRemaining } from '@/store/useAccessStore';
import { fetchAbilityReport, fetchLearningPath, fetchCourses, fetchProjects, getRecommendedCourses, fetchBanners, fetchDirections, fetchLearningStats } from '@/services/api';
import type { Course, Project } from '@/types/index';
import type { CourseRecommendation, BannerItem, DirectionItem } from '@/services/api';
import styles from './index.module.scss';

/** 学习方向 → 课程阶段映射（用于过滤课程） */
const DIRECTION_TOPIC_MAP: Record<string, string> = {
  '阶段一 · AI 大模型基础': '大模型基础',
  '阶段二 · Agent 基础概念': 'Agent基础',
  '阶段三 · Agent 开发实战': '开发实战',
  '阶段四 · 多 Agent 系统': '多Agent',
  '阶段五 · 优化和部署': '优化部署',
  '阶段六 · 项目实战': '项目实战',
  '阶段七 · 求职备战': '求职备战',
  // 兼容测评推荐方向（assessment_service 返回的方向名）→ 统一从阶段一起步
  '大模型应用开发': '大模型基础',
  '机器学习工程师': '大模型基础',
  '深度学习工程师': '大模型基础',
  '数据科学家': '大模型基础',
  'AI 应用开发': '大模型基础',
  'AI 工程师': '大模型基础',
  '计算机视觉工程师': '大模型基础',
  // 零基础能力测评推荐方向（带推荐后缀）
  '从零开始学AI（小白推荐）': '大模型基础',
  'AI办公提效（职场推荐）': '大模型基础',
  'AI项目实战（进阶推荐）': '开发实战',
  '系统掌握AI应用（深度推荐）': '优化部署',
};

/** 课程阶段 / 难度 → 中文展示 */
const TOPIC_CN_MAP: Record<string, string> = {
  '大模型基础': '大模型基础',
  'Agent基础': 'Agent 概念',
  '开发实战': '开发实战',
  '多Agent': '多 Agent',
  '优化部署': '优化部署',
  '项目实战': '项目实战',
  '求职备战': '求职备战',
  'beginner': '入门',
  'intermediate': '进阶',
  'advanced': '高级',
};

/** AI 工具入口（不再用 emoji 当图标，靠标题层级 + 标签区分） */
const AI_TOOLS = [
  { key: 'tutor', name: 'AI 导师', desc: '对话式答疑，按你的进度讲解', tag: '实时问答', url: '/pages/tutor/index' },
  { key: 'assessment', name: '能力分析', desc: '15 分钟定位你的 AI 水平', tag: '精准评估', url: '/pages/assessment/index' },
  { key: 'recommend', name: '课程推荐', desc: '按目标方向匹配学习内容', tag: '智能匹配', url: '' }
];

const HomePage: React.FC = () => {
  const { nickname, avatar, targetDirection, isLoggedIn } = useUserStore();
  // 试用期即将到期提醒横幅（试用到期的全屏锁定由 AccessGate 遮罩接管，此处不重复）
  const accessStatus = useAccessStore((s) => s.status);
  const warnExpiring = accessStatus?.warn_expiring ?? false;
  const goDeposit = () => Taro.navigateTo({ url: '/pages/deposit/index' });
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
  const [loaded, setLoaded] = useState(false);

  const firstShow = useRef(true);

  // 仅挂载时加载一次，后续靠 useDidShow 刷新；loadData 只用 setState/store
  /* eslint-disable react-hooks/exhaustive-deps -- 仅挂载时加载一次，后续靠 useDidShow 刷新 */
  useEffect(() => {
    loadData();
  }, []);
  /* eslint-enable react-hooks/exhaustive-deps */

  // 每次页面显示时刷新（从学习路径/课程页标记完成后返回，路径进度同步更新）；
  // 首次显示由 useEffect 承担，这里跳过避免重复请求
  useDidShow(() => {
    if (firstShow.current) { firstShow.current = false; return; }
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
    } finally {
      setLoaded(true);
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

  const onToolClick = (key: string, url: string) => {
    if (key === 'recommend') handleCourseRecommend();
    else if (url) Taro.navigateTo({ url });
  };

  return (
    <Fragment>
      <ScrollView className={styles.page} scrollY>
        {/* ---------- Hero：左文案 + 右统计（非对称，避免"居中标题 + 三等分卡片"的默认感） ---------- */}
        <View className={styles.hero}>
          <View className={styles.heroGlow} aria-hidden />
          <View className={styles.heroGrid} aria-hidden />
          <View className={styles.heroInner}>
            <View className={styles.heroLeft}>
              <Text className={styles.eyebrow}>
                {targetDirection ? `目标方向 · ${targetDirection}` : '还未设置目标方向'}
              </Text>
              <Text className={styles.title}>
                {isLoggedIn ? `${nickname || '同学'}，继续你的 AI 学习` : '开始你的 AI 学习'}
              </Text>
              <Text className={styles.subtitle}>
                七个阶段从大模型基础到求职备战，课程、实战项目与 AI 导师都在一条路径上。
              </Text>
              <View className={styles.ctaRow}>
                <Button size="md" onClick={handleStartAssessment}>
                  {abilityReport ? '重新测评' : '开始能力测评'}
                </Button>
                <Button tone="ghost" size="md" onClick={() => Taro.navigateTo({ url: '/pages/tutor/index' })}>
                  问 AI 导师
                </Button>
              </View>
            </View>

            <View className={styles.heroStats}>
              <Stat value={stats.learningDays} label="学习天数" />
              <View className={styles.statDivider} />
              <Stat value={stats.totalMinutes} label="学习时长 / 分钟" />
              <View className={styles.statDivider} />
              <Stat value={stats.completedProjects} label="完成项目" />
            </View>
          </View>
        </View>

        {/* 试用期即将到期提醒 */}
        {warnExpiring && accessStatus && (
          <View className={styles.trialWarn} onClick={goDeposit}>
            <Tag tone="warning">试用提醒</Tag>
            <Text className={styles.trialWarnText}>
              还剩 {formatTrialRemaining(accessStatus.trial_remaining_seconds)}，到期未缴押金将暂停使用
            </Text>
            <Text className={styles.trialWarnAction}>去缴纳 →</Text>
          </View>
        )}

        {/* Banner 轮播 */}
        {banners.length > 0 && (
          <Reveal>
            <View className={styles.bannerWrap}>
              <Swiper
                className={styles.banner}
                indicatorColor="rgba(255,255,255,0.22)"
                indicatorActiveColor="#7c88e8"
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
          </Reveal>
        )}

        {/* ---------- AI 智能工具：bento（3 格，其中 1 格用强调色表面；不再三张彩色渐变） ---------- */}
        <Reveal>
          <View className={styles.section}>
            <SectionHeader title="AI 智能工具" hint="三件事：问、测、配" />
            <View className={styles.toolGrid}>
              {AI_TOOLS.map((tool, i) => (
                <Panel
                  key={tool.key}
                  spotlight
                  className={`${styles.toolCard} ${i === 0 ? styles.toolCardAccent : ''}`}
                >
                  <View className={styles.toolHead} onClick={() => onToolClick(tool.key, tool.url)}>
                    <Text className={styles.toolName}>{tool.name}</Text>
                    <Tag tone={i === 0 ? 'accent' : 'neutral'}>{tool.tag}</Tag>
                  </View>
                  <Text className={styles.toolDesc}>{tool.desc}</Text>
                </Panel>
              ))}
            </View>
          </View>
        </Reveal>

        {/* 能力测评 */}
        <Reveal>
          <View className={styles.section}>
            {abilityReport ? (
              <AssessmentCard
                overallScore={abilityReport.overallScore}
                level={abilityReport.level}
                direction={abilityReport.recommendedDirection}
                onClick={handleStartAssessment}
              />
            ) : (
              <Panel spotlight className={styles.assessmentEntry} padded={false}>
                <View className={styles.assessmentInner} onClick={handleStartAssessment}>
                  <View className={styles.assessmentText}>
                    <Text className={styles.assessmentTitle}>还没有能力画像</Text>
                    <Text className={styles.assessmentDesc}>
                      15 分钟测评，产出能力雷达与推荐方向，首页与学习路径会据此调整。
                    </Text>
                  </View>
                  <Button size="sm">开始测评</Button>
                </View>
              </Panel>
            )}
          </View>
        </Reveal>

        {/* 学习方向（点击后过滤课程） */}
        {directions.length > 0 && (
          <Reveal>
            <View className={styles.section}>
              <SectionHeader
                title="学习方向"
                actionText="查看课程"
                onAction={() => Taro.switchTab({ url: '/pages/learn/index' })}
              />
              <ScrollView className={styles.directionScroll} scrollX>
                {directions.map((dir) => (
                  <View
                    key={dir.id}
                    className={styles.directionCard}
                    onClick={() => handleSelectDirection(dir.name)}
                  >
                    <Text className={styles.directionName}>{dir.name}</Text>
                    <Text className={styles.directionDesc}>{dir.description}</Text>
                    <Text className={styles.directionArrow}>→</Text>
                  </View>
                ))}
              </ScrollView>
            </View>
          </Reveal>
        )}

        {/* 学习路径 */}
        {currentPath && (
          <Reveal>
            <View className={styles.section}>
              <SectionHeader title="我的学习路径" actionText="查看全部" onAction={handleViewPath} />
              <PathCard path={currentPath} onClick={handleViewPath} />
            </View>
          </Reveal>
        )}

        {/* AI 推荐课程（基于用户目标方向） */}
        {aiRecommendations.length > 0 && (
          <Reveal>
            <View className={styles.section}>
              <SectionHeader title="AI 推荐课程" hint="按你的目标方向匹配" actionText="更多" onAction={handleCourseRecommend} />
              <View className={styles.recommendList}>
                {aiRecommendations.map((rec, i) => (
                  <View key={i} className={styles.recommendItem} onClick={() => handleViewCourse(rec.id)}>
                    <Text className={styles.recommendItemTitle}>{rec.title}</Text>
                    <View className={styles.recommendItemMeta}>
                      <Text className={styles.recommendMetaText}>
                        {TOPIC_CN_MAP[rec.topic] || rec.topic} · {TOPIC_CN_MAP[rec.difficulty] || rec.difficulty}
                      </Text>
                      <Text className={styles.recommendScore}>{Math.round(rec.score * 100)}%</Text>
                    </View>
                  </View>
                ))}
              </View>
            </View>
          </Reveal>
        )}

        {/* 推荐课程 */}
        {courses.length > 0 && (
          <Reveal>
            <View className={styles.section}>
              <SectionHeader title="推荐课程" actionText="更多" onAction={() => handleViewAll('course')} />
              <View className={styles.courseGrid}>
                {courses.map((course) => (
                  <View key={course.id} className={styles.courseItem}>
                    <CourseCard course={course} onClick={() => handleViewCourse(course.id)} />
                  </View>
                ))}
              </View>
            </View>
          </Reveal>
        )}

        {/* 推荐项目 */}
        {projects.length > 0 && (
          <Reveal>
            <View className={styles.section}>
              <SectionHeader title="推荐项目" actionText="更多" onAction={() => handleViewAll('project')} />
              <View className={styles.projectGrid}>
                {projects.map((project) => (
                  <View key={project.id} className={styles.projectItem}>
                    <ProjectCard project={project} onClick={() => handleViewProject(project.id)} />
                  </View>
                ))}
              </View>
            </View>
          </Reveal>
        )}

        {/* 首屏骨架：数据未回来时给结构一致的占位，而不是空白 */}
        {!loaded && (
          <View className={styles.section}>
            <View className={styles.skeletonRow}>
              <View className={styles.skeletonBlock} />
              <View className={styles.skeletonBlock} />
            </View>
          </View>
        )}

        <View className={styles.footerNote}>
          <Text>智学 AI · 课程 {courses.length} 门 / 项目 {projects.length} 个</Text>
        </View>
      </ScrollView>

      {/* 导语弹窗 + 锁定遮罩（不放 ScrollView 内：微信端 scroll-view 内的 fixed 元素
          会被滚动容器裁剪/失效，导致弹窗不可见；须作为页面的兄弟节点渲染） */}
      <AccessGate />
    </Fragment>
  );
};

export default HomePage;
