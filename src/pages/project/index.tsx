import React, { useCallback, useEffect, useRef, useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro, { useDidShow } from '@tarojs/taro';
import ProjectCard from '@/components/ProjectCard';
import { fetchProjects, fetchProjectCategories } from '@/services/api';
import type { Project } from '@/types/index';
import styles from './index.module.scss';

/** 难度 → 中文 */
const DIFFICULTY_LABEL: Record<string, string> = {
  beginner: '入门',
  intermediate: '进阶',
  advanced: '高级',
  all: '全部',
};

const ProjectPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [categories, setCategories] = useState<{ key: string; label: string }[]>([{ key: 'all', label: '全部' }]);
  const [activeCategory, setActiveCategory] = useState('all');

  const firstShow = useRef(true);

  const loadData = useCallback(async (category?: string) => {
    try {
      const [projectData, catData] = await Promise.all([
        fetchProjects(category === 'all' || category === undefined ? undefined : category),
        fetchProjectCategories(),
      ]);
      setProjects(projectData);
      const cats = catData.map((c: string) => ({ key: c, label: DIFFICULTY_LABEL[c] || c }));
      setCategories([{ key: 'all', label: '全部' }, ...cats]);
    } catch (err) {
      console.error('[Project] load data error:', err);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Tab 页切回时重新拉取（保留当前难度筛选），避免看到旧数据
  useDidShow(() => {
    if (firstShow.current) { firstShow.current = false; return; }
    loadData(activeCategory);
  });

  const handleCategoryChange = async (key: string) => {
    setActiveCategory(key);
    if (key === 'all') {
      try {
        setProjects(await fetchProjects());
      } catch (err) {
        console.error('[Project] filter error:', err);
      }
      return;
    }
    try {
      const data = await fetchProjects(key);
      setProjects(data);
    } catch (err) {
      console.error('[Project] filter error:', err);
    }
  };

  const handleViewProject = (id: string) => {
    Taro.navigateTo({ url: `/pages/projectDetail/index?id=${id}` });
  };

  return (
    <ScrollView className={styles.page} scrollY>
      {/* 分类筛选 */}
      <View className={styles.categoryWrap}>
        <ScrollView className={styles.categoryScroll} scrollX>
          {categories.map((cat) => (
            <View
              key={cat.key}
              className={`${styles.categoryItem} ${activeCategory === cat.key ? styles.categoryActive : ''}`}
              onClick={() => handleCategoryChange(cat.key)}
            >
              <Text className={`${styles.categoryText} ${activeCategory === cat.key ? styles.categoryTextActive : ''}`}>
                {cat.label}
              </Text>
            </View>
          ))}
        </ScrollView>
      </View>

      {/* 项目列表 */}
      <View className={styles.projectList}>
        {projects.map((project) => (
          <View key={project.id} className={styles.projectItem}>
            <ProjectCard project={project} onClick={() => handleViewProject(project.id)} />
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default ProjectPage;