import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Image } from '@tarojs/components';
import Taro, { useDidShow } from '@tarojs/taro';
import { fetchFavorites, removeFavorite } from '@/services/api';
import type { FavoriteItem } from '@/types/index';
import styles from './index.module.scss';

const FavoritesPage: React.FC = () => {
  const [items, setItems] = useState<FavoriteItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const data = await fetchFavorites();
      setItems(data);
    } catch (err) {
      console.error('[Favorites] load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 从详情页返回时刷新（可能取消了收藏）
  useDidShow(() => {
    loadData();
  });

  const handleRemove = async (item: FavoriteItem) => {
    try {
      await removeFavorite(item.id);
      await loadData();
      Taro.showToast({ title: '已取消收藏', icon: 'none' });
    } catch (err) {
      console.error('[Favorites] remove error:', err);
    }
  };

  const handleOpen = (item: FavoriteItem) => {
    Taro.navigateTo({ url: item.detail_path });
  };

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
          <Text className={styles.emptyIcon}>⭐</Text>
          <Text className={styles.emptyText}>还没有收藏，去收藏喜欢的课程或项目吧</Text>
        </View>
      ) : (
        <View className={styles.list}>
          {items.map((item) => (
            <View key={item.id} className={styles.item} onClick={() => handleOpen(item)}>
              {item.cover_img ? (
                <Image className={styles.cover} src={item.cover_img} mode="aspectFill" />
              ) : (
                <View className={styles.coverFallback}>{item.item_type === 'course' ? '📚' : '🛠️'}</View>
              )}
              <View className={styles.info}>
                <Text className={styles.title}>{item.title}</Text>
                <Text className={styles.typeTag}>{item.item_type === 'course' ? '课程' : '项目'}</Text>
              </View>
              <Text className={styles.removeBtn} onClick={(e) => { e.stopPropagation(); handleRemove(item); }}>
                取消收藏
              </Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
};

export default FavoritesPage;
