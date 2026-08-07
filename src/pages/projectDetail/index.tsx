import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Image } from '@tarojs/components';
import Taro from '@tarojs/taro';
import ProgressBar from '@/components/ProgressBar';
import { fetchProjects, advanceProject } from '@/services/api';
import { getDifficultyLabel, getDifficultyColor } from '@/utils/index';
import type { Project } from '@/types/index';
import styles from './index.module.scss';

const ProjectDetailPage: React.FC = () => {
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [advancing, setAdvancing] = useState(false);

  useEffect(() => {
    const loadProject = async () => {
      try {
        const { id } = Taro.getCurrentInstance().router?.params || {};
        const projects = await fetchProjects();
        const found = projects.find((p) => p.id === id);
        setProject(found || null);
      } catch (err) {
        console.error('[ProjectDetail] load error:', err);
      } finally {
        setLoading(false);
      }
    };
    loadProject();
  }, []);

  const handleAdvance = async () => {
    if (!project || advancing) return;
    setAdvancing(true);
    try {
      const updated = await advanceProject(project.id);
      setProject(updated);
    } catch (err) {
      console.error('[ProjectDetail] advance error:', err);
      Taro.showToast({ title: '操作失败，请重试', icon: 'none' });
    } finally {
      setAdvancing(false);
    }
  };

  if (loading) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  if (!project) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>项目不存在</Text>
      </View>
    );
  }

  // 项目分步指南：优先用项目数据里的 steps（含 guide/acceptance/status），否则回退通用
  const steps: { id: number; title: string; desc: string; guide?: string; acceptance?: string; status: 'pending' | 'current' | 'completed' }[] =
    (project.steps && project.steps.length > 0
      ? project.steps.map((s, i) => ({
          id: i + 1,
          title: s.title,
          desc: (s as any).desc || (s as any).description || '',
          guide: (s as any).guide || '',
          acceptance: (s as any).acceptance || '',
          status: ((s as any).status || (i === 0 ? 'current' : 'pending')) as 'pending' | 'current' | 'completed',
        }))
      : [
          { id: 1, title: '环境准备与项目初始化', desc: '安装依赖，创建项目骨架', status: 'completed' as const },
          { id: 2, title: '核心功能实现', desc: '实现主要业务逻辑', status: 'current' as const },
          { id: 3, title: '代码测试与调试', desc: '运行测试，修复 Bug', status: 'pending' as const },
          { id: 4, title: '项目优化与文档', desc: '代码优化，撰写文档', status: 'pending' as const },
          { id: 5, title: '提交与展示', desc: '提交项目，生成作品集', status: 'pending' as const },
        ]);

  const diffColor = getDifficultyColor(project.difficulty);

  return (
    <ScrollView className={styles.page} scrollY>
      <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
        <Text className={styles.navBack}>← 返回</Text>
      </View>
      <Image className={styles.cover} src={project.coverImg} mode="aspectFill" />
      <View className={styles.body}>
        <Text className={styles.title}>{project.title}</Text>
        <Text className={styles.desc}>{project.description}</Text>

        <View className={styles.tags}>
          <View className={styles.tag} style={{ backgroundColor: `${diffColor}18` }}>
            <Text className={styles.tagText} style={{ color: diffColor }}>
              {getDifficultyLabel(project.difficulty)}
            </Text>
          </View>
          <View className={styles.tag}>
            <Text className={styles.tagText}>{project.estimatedHours} 小时</Text>
          </View>
          {project.isFree ? (
            <View className={styles.freeTag}>
              <Text className={styles.freeTagText}>免费</Text>
            </View>
          ) : (
            <View className={styles.proTag}>
              <Text className={styles.proTagText}>¥{project.price}</Text>
            </View>
          )}
        </View>

        <View className={styles.techStack}>
          <Text className={styles.techLabel}>技术栈</Text>
          <View className={styles.techTags}>
            {project.techStack.map((tech) => (
              <View key={tech} className={styles.techTag}>
                <Text className={styles.techTagText}>{tech}</Text>
              </View>
            ))}
          </View>
        </View>

        {project.progress > 0 && (
          <View className={styles.progressSection}>
            <View className={styles.progressHeader}>
              <Text className={styles.progressLabel}>项目进度</Text>
              <Text className={styles.progressValue}>{project.progress}%</Text>
            </View>
            <ProgressBar percent={project.progress} height={8} />
          </View>
        )}

        <Text className={styles.sectionTitle}>项目步骤</Text>
        <View className={styles.stepList}>
          {steps.map((step) => (
            <View key={step.id} className={styles.stepItem}>
              <View className={styles.stepNumber}>
                {step.status === 'completed' && <Text className={styles.stepCheck}>✅</Text>}
                {step.status === 'current' && <Text className={styles.stepCurrent}>{step.id}</Text>}
                {step.status === 'pending' && <Text className={styles.stepPending}>{step.id}</Text>}
              </View>
              <View className={styles.stepContent}>
                <Text className={styles.stepTitle}>{step.title}</Text>
                <Text className={styles.stepDesc}>{step.desc}</Text>
                {step.status === 'current' && step.guide && (
                  <View className={styles.stepGuide}>
                    <Text className={styles.stepGuideLabel}>📋 操作指引</Text>
                    <Text className={styles.stepGuideText}>{step.guide}</Text>
                  </View>
                )}
                {step.status === 'current' && step.acceptance && (
                  <View className={styles.stepAcceptance}>
                    <Text className={styles.stepAcceptanceLabel}>✅ 验收标准</Text>
                    <Text className={styles.stepAcceptanceText}>{step.acceptance}</Text>
                  </View>
                )}
              </View>
            </View>
          ))}
        </View>

        <View className={styles.button} onClick={handleAdvance}>
          <Text className={styles.buttonText}>
            {advancing
              ? '处理中...'
              : project.status === 'completed'
                ? '🎉 项目已完成'
                : project.progress > 0
                  ? '完成当前步骤'
                  : '开始项目'}
          </Text>
        </View>
      </View>
    </ScrollView>
  );
};

export default ProjectDetailPage;