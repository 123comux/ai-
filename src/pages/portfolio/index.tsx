import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { fetchPortfolio } from '@/services/api';
import type { PortfolioItem } from '@/types/index';
import styles from './index.module.scss';

const PortfolioPage: React.FC = () => {
  const [items, setItems] = useState<PortfolioItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const data = await fetchPortfolio();
      setItems(data);
    } catch (err) {
      console.error('[Portfolio] load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  return (
    <ScrollView className={styles.page} scrollY>
      <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
        <Text className={styles.navBack}>← 返回</Text>
      </View>

      {items.length === 0 ? (
        <View className={styles.empty}>
          <Text className={styles.emptyIcon}>📁</Text>
          <Text className={styles.emptyText}>还没有作品，去完成一个项目吧</Text>
        </View>
      ) : (
        <View className={styles.list}>
          {items.map((item) => (
            <View
              key={item.id}
              className={styles.card}
              onClick={() => Taro.navigateTo({ url: `/pages/projectDetail/index?id=${item.id}` })}
            >
              <View className={styles.cardHeader}>
                <Text className={styles.title}>{item.title}</Text>
                <Text
                  className={`${styles.statusBadge} ${item.status === 'completed' ? styles.statusDone : styles.statusDoing}`}
                >
                  {item.status === 'completed' ? '已完成' : '进行中'}
                </Text>
              </View>
              <Text className={styles.desc}>{item.description}</Text>
              {item.techStack.length > 0 && (
                <View className={styles.techList}>
                  {item.techStack.map((tech, i) => (
                    <Text key={i} className={styles.techTag}>{tech}</Text>
                  ))}
                </View>
              )}
              <Text className={styles.progressInfo}>
                {item.completedSteps}/{item.totalSteps} 步完成
              </Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
};

export default PortfolioPage;
