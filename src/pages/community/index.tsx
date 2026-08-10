import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Input, Textarea } from '@tarojs/components';
import Taro, { useDidShow, useShareAppMessage } from '@tarojs/taro';
import {
  doCheckin, fetchCheckinStatus, fetchLeaderboard,
  fetchPosts, createPost,
} from '@/services/api';
import styles from './index.module.scss';

const TABS = [
  { key: 'checkin', label: '打卡' },
  { key: 'rank', label: '排行榜' },
  { key: 'community', label: '社区' },
];

// 小程序专属：右上角转发分享（分享学习激励页，拉新裂变）
useShareAppMessage(() => ({
  title: '一起学 AI，每日打卡领提示词模板！',
  path: '/pages/community/index',
}));

const CommunityPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('checkin');
  const [checkin, setCheckin] = useState<{ today_checked: boolean; streak: number; recent_dates: string[] }>({ today_checked: false, streak: 0, recent_dates: [] });
  const [ranking, setRanking] = useState<{ ranking: any[]; my_rank: number | null; my_total_minutes: number }>({ ranking: [], my_rank: null, my_total_minutes: 0 });
  const [posts, setPosts] = useState<any[]>([]);
  const [showSheet, setShowSheet] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const loadCheckin = async () => {
    try { setCheckin(await fetchCheckinStatus()); } catch (e) { console.error('[Community] checkin', e); }
  };
  const loadRank = async () => {
    try { setRanking(await fetchLeaderboard(10)); } catch (e) { console.error('[Community] rank', e); }
  };
  const loadPosts = async () => {
    try { setPosts(await fetchPosts()); } catch (e) { console.error('[Community] posts', e); }
  };

  const loadAll = () => { loadCheckin(); loadRank(); loadPosts(); };
  useEffect(() => { loadAll(); }, []);
  useDidShow(() => { loadAll(); });

  const handleCheckin = async () => {
    try {
      const r = await doCheckin();
      setCheckin({ today_checked: true, streak: r.streak, recent_dates: [r.checkin_date] });
      Taro.showToast({ title: `打卡成功 · 连续 ${r.streak} 天`, icon: 'success' });
      loadRank();
    } catch (err: any) {
      Taro.showToast({ title: err?.message || '打卡失败', icon: 'none' });
    }
  };

  const handleCreatePost = async () => {
    if (!title.trim()) { Taro.showToast({ title: '请输入标题', icon: 'none' }); return; }
    try {
      await createPost({ title: title.trim(), content: content.trim(), category: '提问' });
      setTitle(''); setContent(''); setShowSheet(false);
      Taro.showToast({ title: '发布成功', icon: 'success' });
      loadPosts();
    } catch (e) { console.error('[Community] create post', e); }
  };

  const handleOpenPost = (id: number) => {
    Taro.navigateTo({ url: `/pages/communityPost/index?id=${id}` });
  };

  const rankLabel = (i: number) => i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}`;

  return (
    <View className={styles.page}>
      <ScrollView scrollY style={{ height: '100%' }}>
        <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
          <Text className={styles.navBack}>← 返回</Text>
        </View>

        <View className={styles.tabs}>
          {TABS.map((t) => (
            <View
              key={t.key}
              className={`${styles.tab} ${activeTab === t.key ? styles.tabActive : ''}`}
              onClick={() => setActiveTab(t.key)}
            >
              <Text>{t.label}</Text>
            </View>
          ))}
        </View>

        {activeTab === 'checkin' && (
          <View className={styles.checkinCard}>
            <Text className={styles.checkinDate}>今日 {new Date().toLocaleDateString('zh-CN')}</Text>
            <Text className={styles.checkinTitle}>每日 AI 学习打卡</Text>
            <View className={styles.streakRow}>
              <Text className={styles.streakNum}>{checkin.streak}</Text>
              <Text className={styles.streakLabel}>连续打卡天数</Text>
            </View>
            <View
              className={`${styles.checkinBtn} ${checkin.today_checked ? styles.checkinBtnDone : ''}`}
              onClick={handleCheckin}
            >
              <Text className={checkin.today_checked ? styles.checkinBtnDoneText : styles.checkinBtnText}>
                {checkin.today_checked ? '✅ 今日已打卡' : '今日打卡'}
              </Text>
            </View>
          </View>
        )}

        {activeTab === 'rank' && (
          <View className={styles.section}>
            <Text className={styles.sectionTitle}>学习排行榜（按学习时长）</Text>
            {ranking.my_rank && (
              <View className={styles.myRank}>
                <Text className={styles.rankName}>我的排名：第 {ranking.my_rank} 名</Text>
                <Text className={styles.rankMinutes}>{ranking.my_total_minutes} 分钟</Text>
              </View>
            )}
            {ranking.ranking.map((r, i) => (
              <View key={r.id} className={styles.rankItem}>
                <Text className={`${styles.rankNum} ${i === 0 ? styles.rankNumTop1 : i === 1 ? styles.rankNumTop2 : i === 2 ? styles.rankNumTop3 : ''}`}>{rankLabel(i)}</Text>
                <Text className={styles.rankName}>{r.nickname || '匿名用户'}</Text>
                <Text className={styles.rankMinutes}>{r.total_minutes} 分钟 · {r.watched_videos} 个视频</Text>
              </View>
            ))}
          </View>
        )}

        {activeTab === 'community' && (
          <View className={styles.postList}>
            {posts.length === 0 ? (
              <View className={styles.empty}><Text className={styles.emptyText}>还没有帖子，来发第一帖吧</Text></View>
            ) : posts.map((p) => (
              <View key={p.id} className={styles.postItem} onClick={() => handleOpenPost(p.id)}>
                <Text className={styles.postTitle}>{p.title}</Text>
                <Text className={styles.postContent}>{p.content}</Text>
                <View className={styles.postMeta}>
                  <Text className={styles.postCategory}>{p.category}</Text>
                  <Text>{p.nickname || '匿名'}</Text>
                  <Text>💬 {p.reply_count}</Text>
                  <Text>👍 {p.likes}</Text>
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>

      {activeTab === 'community' && (
        <View className={styles.addBtn} onClick={() => setShowSheet(true)}>
          <Text className={styles.addBtnText}>+ 发帖</Text>
        </View>
      )}

      {showSheet && (
        <>
          <View className={styles.mask} onClick={() => setShowSheet(false)} />
          <View className={styles.sheet}>
            <Text className={styles.sheetTitle}>发布提问</Text>
            <Input className={styles.input} placeholder="标题" value={title} onInput={(e) => setTitle(e.detail.value)} />
            <Textarea className={styles.textarea} placeholder="描述你的问题" value={content} onInput={(e) => setContent(e.detail.value)} />
            <View className={styles.sheetActions}>
              <View className={styles.btnCancel} onClick={() => setShowSheet(false)}>
                <Text className={styles.btnCancelText}>取消</Text>
              </View>
              <View className={styles.btnSave} onClick={handleCreatePost}>
                <Text className={styles.btnSaveText}>发布</Text>
              </View>
            </View>
          </View>
        </>
      )}
    </View>
  );
};

export default CommunityPage;
