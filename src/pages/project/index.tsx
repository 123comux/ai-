import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import ProjectCard from '@/components/ProjectCard';
import { fetchProjects, fetchProjectCategories } from '@/services/api';
import type { Project } from '@/types/index';
import styles from './index.module.scss';

const ProjectPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [categories, setCategories] = useState<{ key: string; label: string }[]>([]);
  const [activeCategory, setActiveCategory] = useState('all');

  useEffect(() => {
    const loadData = async () => {
      try {
        const [projectData, catData] = await Promise.all([
          fetchProjects(),
          fetchProjectCategories(),
        ]);
        setProjects(projectData);
        setCategories(catData.map((c: string) => ({ key: c, label: c })));
      } catch (err) {
        console.error('[Project] load data error:', err);
      }
    };
    loadData();
  }, []);

  const handleCategoryChange = async (key: string) => {
    setActiveCategory(key);
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