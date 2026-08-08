import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Input, Textarea } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { fetchGoals, createGoal, updateGoal, deleteGoal } from '@/services/api';
import type { Goal } from '@/types/index';
import styles from './index.module.scss';

const GoalsPage: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [showSheet, setShowSheet] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [targetDate, setTargetDate] = useState('');

  const loadData = async () => {
    try {
      const data = await fetchGoals();
      setGoals(data);
    } catch (err) {
      console.error('[Goals] load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAdd = async () => {
    if (!title.trim()) {
      Taro.showToast({ title: '请输入目标标题', icon: 'none' });
      return;
    }
    try {
      await createGoal({ title: title.trim(), description: description.trim(), target_date: targetDate.trim() });
      setTitle('');
      setDescription('');
      setTargetDate('');
      setShowSheet(false);
      await loadData();
    } catch (err) {
      console.error('[Goals] add error:', err);
      Taro.showToast({ title: '添加失败', icon: 'none' });
    }
  };

  const handleToggle = async (goal: Goal) => {
    try {
      await updateGoal(goal.id, { status: goal.status === 'done' ? 'pending' : 'done' });
      await loadData();
    } catch (err) {
      console.error('[Goals] toggle error:', err);
    }
  };

  const handleDelete = async (goal: Goal) => {
    try {
      await deleteGoal(goal.id);
      await loadData();
    } catch (err) {
      console.error('[Goals] delete error:', err);
    }
  };

  if (loading) {
    return (
      <View className={styles.page}>
        <Text className={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  return (
    <View className={styles.page}>
      <ScrollView scrollY style={{ height: '100%' }}>
        <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
          <Text className={styles.navBack}>← 返回</Text>
        </View>

        {goals.length === 0 ? (
          <View className={styles.empty}>
            <Text className={styles.emptyIcon}>🎯</Text>
            <Text className={styles.emptyText}>还没有学习目标，点击下方按钮添加</Text>
          </View>
        ) : (
          <View className={styles.list}>
            {goals.map((goal) => (
              <View key={goal.id} className={styles.item}>
                <View className={styles.itemHeader}>
                  <View
                    className={`${styles.checkbox} ${goal.status === 'done' ? styles.checkboxDone : ''}`}
                    onClick={() => handleToggle(goal)}
                  >
                    {goal.status === 'done' ? '✓' : ''}
                  </View>
                  <Text className={`${styles.title} ${goal.status === 'done' ? styles.titleDone : ''}`}>
                    {goal.title}
                  </Text>
                  <Text className={styles.deleteBtn} onClick={() => handleDelete(goal)}>删除</Text>
                </View>
                {goal.description && <Text className={styles.desc}>{goal.description}</Text>}
                {goal.target_date && <Text className={styles.targetDate}>📅 {goal.target_date}</Text>}
              </View>
            ))}
          </View>
        )}
      </ScrollView>

      <View className={styles.addBtn} onClick={() => setShowSheet(true)}>
        <Text className={styles.addBtnText}>+ 添加目标</Text>
      </View>

      {showSheet && (
        <>
          <View className={styles.mask} onClick={() => setShowSheet(false)} />
          <View className={styles.sheet}>
            <Text className={styles.sheetTitle}>添加学习目标</Text>
            <Input
              className={styles.input}
              placeholder="目标标题"
              value={title}
              onInput={(e) => setTitle(e.detail.value)}
            />
            <Textarea
              className={styles.textarea}
              placeholder="目标描述（可选）"
              value={description}
              onInput={(e) => setDescription(e.detail.value)}
            />
            <Input
              className={styles.dateInput}
              placeholder="目标日期，如 2026-09-30（可选）"
              value={targetDate}
              onInput={(e) => setTargetDate(e.detail.value)}
            />
            <View className={styles.sheetActions}>
              <View className={styles.btnCancel} onClick={() => setShowSheet(false)}>
                <Text className={styles.btnCancelText}>取消</Text>
              </View>
              <View className={styles.btnSave} onClick={handleAdd}>
                <Text className={styles.btnSaveText}>保存</Text>
              </View>
            </View>
          </View>
        </>
      )}
    </View>
  );
};

export default GoalsPage;
