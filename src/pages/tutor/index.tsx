import React, { useState, useRef, useEffect } from 'react';
import { View, Text, ScrollView, Input } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { askTutor, getAIModelsInfo } from '@/services/api';
import styles from './index.module.scss';

const TutorPage: React.FC = () => {
  const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'ai'; content: string }[]>([
    { role: 'ai', content: '你好！我是你的 AI 学习导师，有什么问题可以问我～' },
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [modelLoading, setModelLoading] = useState(true); // 模型预加载状态
  const scrollRef = useRef<ScrollView>(null);

  // 页面加载时预加载 AI 模型，避免首次提问超时
  useEffect(() => {
    getAIModelsInfo()
      .then(() => {
        setModelLoading(false);
        console.log('[Tutor] Model preloaded');
      })
      .catch(() => {
        setModelLoading(false);
        console.warn('[Tutor] Model preload failed, will load on first request');
      });
  }, []);

  const handleSendMessage = async () => {
    const text = chatInput.trim();
    if (!text || chatLoading || modelLoading) return;
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

  const handleBack = () => {
    Taro.navigateBack();
  };

  return (
    <View className={styles.page}>
      {/* 顶部导航 */}
      <View className={styles.navBar}>
        <Text className={styles.navBack} onClick={handleBack}>← 返回</Text>
        <Text className={styles.navTitle}>AI 学习导师</Text>
        <View className={styles.navRight} />
      </View>

      {/* 消息列表：高度用 calc 精确计算，避免 flex 挤压 */}
      <ScrollView
        className={styles.messages}
        scrollY
        ref={scrollRef}
        scrollWithAnimation
        scrollTop={99999}
      >
        {modelLoading && (
          <View className={`${styles.msg} ${styles.msgAi}`}>
            <View className={styles.bubbleAi}>
              <Text className={styles.bubbleText}>正在加载 AI 模型（约需 60 秒），请稍候...</Text>
            </View>
          </View>
        )}
        {chatMessages.map((msg, i) => (
          <View
            key={i}
            className={`${styles.msg} ${msg.role === 'user' ? styles.msgUser : styles.msgAi}`}
          >
            <View className={msg.role === 'user' ? styles.bubbleUser : styles.bubbleAi}>
              <Text className={styles.bubbleText}>{msg.content}</Text>
            </View>
          </View>
        ))}
        {chatLoading && (
          <View className={`${styles.msg} ${styles.msgAi}`}>
            <View className={styles.bubbleAi}>
              <Text className={styles.bubbleText}>正在思考...</Text>
            </View>
          </View>
        )}
      </ScrollView>

      {/* 底部输入栏：固定在底部，不参与页面 flex 计算 */}
      <View className={styles.inputBar}>
        <Input
          className={styles.input}
          placeholder="输入你的问题..."
          value={chatInput}
          onInput={(e) => setChatInput(e.detail.value)}
          onConfirm={handleSendMessage}
          disabled={chatLoading || modelLoading}
          confirmType="send"
        />
        <View
          className={`${styles.sendBtn} ${(chatLoading || modelLoading) ? styles.sendBtnDisabled : ''}`}
          onClick={handleSendMessage}
        >
          <Text className={styles.sendBtnText}>发送</Text>
        </View>
      </View>
    </View>
  );
};

export default TutorPage;
