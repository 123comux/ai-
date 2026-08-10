import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Input } from '@tarojs/components';
import Taro, { useDidShow } from '@tarojs/taro';
import { fetchPostDetail, replyPost, likePost } from '@/services/api';
import styles from './index.module.scss';

const CommunityPostPage: React.FC = () => {
  const [post, setPost] = useState<any>(null);
  const [replies, setReplies] = useState<any[]>([]);
  const [replyText, setReplyText] = useState('');

  const loadData = async () => {
    try {
      const { id } = Taro.getCurrentInstance().router?.params || {};
      if (!id) return;
      const data = await fetchPostDetail(Number(id));
      setPost(data.post);
      setReplies(data.replies);
    } catch (err) {
      console.error('[CommunityPost] load error:', err);
    }
  };

  useEffect(() => { loadData(); }, []);
  useDidShow(() => { loadData(); });

  const handleReply = async () => {
    if (!replyText.trim() || !post) return;
    try {
      await replyPost(post.id, replyText.trim());
      setReplyText('');
      await loadData();
    } catch (err: any) {
      Taro.showToast({ title: err?.message || '回复失败', icon: 'none' });
    }
  };

  const handleLike = async () => {
    if (!post) return;
    try {
      const r = await likePost(post.id);
      setPost({ ...post, likes: r.likes });
    } catch (e) { console.error('[CommunityPost] like', e); }
  };

  return (
    <View className={styles.page}>
      <ScrollView scrollY style={{ height: '100%' }}>
        <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
          <Text className={styles.navBack}>← 返回</Text>
        </View>

        {post && (
          <View className={styles.card}>
            <Text className={styles.title}>{post.title}</Text>
            <View className={styles.meta}>
              <Text className={styles.category}>{post.category}</Text>
              <Text>{post.nickname || '匿名'}</Text>
              <Text>👍 {post.likes}</Text>
            </View>
            <Text className={styles.content}>{post.content}</Text>
            <View className={styles.likeBtn} onClick={handleLike}>👍 点赞</View>
          </View>
        )}

        <Text className={styles.sectionTitle}>回复（{replies.length}）</Text>
        <View className={styles.replyList}>
          {replies.length === 0 ? (
            <View className={styles.empty}>暂无回复，来抢沙发</View>
          ) : replies.map((r) => (
            <View key={r.id} className={styles.replyItem}>
              <Text className={styles.replyName}>{r.nickname || '匿名'}</Text>
              <Text className={styles.replyContent}>{r.content}</Text>
            </View>
          ))}
        </View>
      </ScrollView>

      <View className={styles.replyBar}>
        <Input
          className={styles.replyInput}
          placeholder="写下你的回复..."
          value={replyText}
          onInput={(e) => setReplyText(e.detail.value)}
          confirmType="send"
          onConfirm={handleReply}
        />
        <View className={styles.replyBtn} onClick={handleReply}>
          <Text className={styles.replyBtnText}>回复</Text>
        </View>
      </View>
    </View>
  );
};

export default CommunityPostPage;
