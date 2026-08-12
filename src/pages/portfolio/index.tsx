import React, { useEffect, useRef, useState } from 'react';
import { View, Text, ScrollView, Button } from '@tarojs/components';
import Taro, { useShareAppMessage } from '@tarojs/taro';
import { fetchPortfolio } from '@/services/api';
import type { PortfolioItem } from '@/types/index';
import styles from './index.module.scss';

const PortfolioPage: React.FC = () => {
  const [items, setItems] = useState<PortfolioItem[]>([]);
  const [loading, setLoading] = useState(true);

  // 一键分享作品：点分享时写 ref，openType=share 面板读取
  const shareRef = useRef({ title: '我的 AI 学习作品集', path: '/pages/portfolio/index' });
  useShareAppMessage(() => shareRef.current);

  const handleShareItem = (item: PortfolioItem) => {
    shareRef.current = {
      title: `我用 AI 完成了「${item.title}」${item.status === 'completed' ? '' : '（进行中）'}，${item.completedSteps}/${item.totalSteps} 步`,
      path: '/pages/portfolio/index',
    };
  };

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
                <View className={styles.cardHeaderRight}>
                  <Text
                    className={`${styles.statusBadge} ${item.status === 'completed' ? styles.statusDone : styles.statusDoing}`}
                  >
                    {item.status === 'completed' ? '已完成' : '进行中'}
                  </Text>
                  <Button className={styles.shareBtn} openType="share" onClick={() => handleShareItem(item)}>
                    分享
                  </Button>
                </View>
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
