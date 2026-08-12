import React, { useState } from 'react';
import { View, Text, ScrollView, Input, Picker, Button, Image } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useUserStore } from '@/store/useUserStore';
import { uploadAvatar } from '@/services/api';
import styles from './index.module.scss';

const GRADES = ['大一', '大二', '大三', '大四', '研究生'];
const MAJORS = ['计算机科学与技术', '软件工程', '人工智能', '数据科学', '电子信息', '自动化', '其他'];
const DIRECTIONS = ['AI 算法工程师', 'AI 产品经理', 'AIGC 应用人才', '数据分析工程师', 'AI 应用开发', '大模型应用开发'];

// 微信"头像昵称填写能力"（基础库 2.21.2+）仅在小程序端可用
const IS_WEAPP = process.env.TARO_ENV === 'weapp';

const SettingsPage: React.FC = () => {
  const { nickname, avatar, grade, major, targetDirection, setUser, logout, updateProfile } = useUserStore();
  const [editing, setEditing] = useState(false);

  const handleSave = async () => {
    try {
      setUser({ nickname, grade, major, targetDirection });
      await Taro.setStorageSync('user_info', { nickname, grade, major, targetDirection });
      // 同步昵称到后端（不传 avatar，store 内保留当前头像，避免误清）
      await updateProfile(nickname);
      setEditing(false);
      Taro.showToast({ title: '已保存', icon: 'success' });
    } catch (err) {
      console.error('[Settings] save error:', err);
      Taro.showToast({ title: '保存失败，请重试', icon: 'none' });
    }
  };

  const handleClearCache = () => {
    Taro.showModal({
      title: '清除缓存',
      content: '将清除本地缓存数据，确定继续吗？',
      success: (res) => {
        if (res.confirm) {
          try {
            Taro.clearStorageSync();
            Taro.showToast({ title: '已清除', icon: 'success' });
          } catch (err) {
            console.error('[Settings] clear cache error:', err);
          }
        }
      },
    });
  };

  const handleLogout = () => {
    Taro.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          logout();
          Taro.showToast({ title: '已退出', icon: 'none' });
        }
      },
    });
  };

  // 头像选择：open-type=chooseAvatar 用户主动授权微信头像，先上传换持久 URL 再回传后端
  const handleAvatar = async (url: string) => {
    if (!url) return;
    try {
      Taro.showLoading({ title: '更新中...', mask: true });
      const finalUrl = /^https?:\/\//.test(url) ? url : await uploadAvatar(url);
      await updateProfile(nickname, finalUrl);
      Taro.hideLoading();
      Taro.showToast({ title: '头像已更新', icon: 'success' });
    } catch (err: any) {
      Taro.hideLoading();
      Taro.showToast({ title: err?.message || '更新失败', icon: 'none' });
    }
  };

  if (!editing) {
    return (
      <ScrollView className={styles.page} scrollY>
        <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
          <Text className={styles.navBack}>← 返回</Text>
        </View>

        <View className={styles.card}>
          <View className={styles.row} onClick={() => setEditing(true)}>
            <Text className={styles.rowLabel}>个人资料</Text>
            <Text className={styles.rowArrow}>编辑 →</Text>
          </View>
          <View className={styles.row}>
            <Text className={styles.rowLabel}>昵称</Text>
            <Text className={styles.value}>{nickname}</Text>
          </View>
          <View className={styles.row}>
            <Text className={styles.rowLabel}>年级</Text>
            <Text className={styles.value}>{grade}</Text>
          </View>
          <View className={styles.row}>
            <Text className={styles.rowLabel}>专业</Text>
            <Text className={styles.value}>{major}</Text>
          </View>
          <View className={styles.row}>
            <Text className={styles.rowLabel}>目标方向</Text>
            <Text className={styles.value}>{targetDirection}</Text>
          </View>
        </View>

        <View className={styles.card}>
          {IS_WEAPP ? (
            <View className={styles.row}>
              <Text className={styles.rowLabel}>更换头像</Text>
              <Button
                className={styles.avatarBtn}
                openType="chooseAvatar"
                onChooseAvatar={(e: any) => handleAvatar(e?.detail?.avatarUrl || '')}
              >
                {avatar ? (
                  <Image className={styles.avatarThumb} src={avatar} mode="aspectFill" />
                ) : (
                  <Text className={styles.avatarThumbPlaceholder}>👤</Text>
                )}
                <Text className={styles.rowArrow}>→</Text>
              </Button>
            </View>
          ) : (
            <View className={styles.row} onClick={() => Taro.showToast({ title: 'H5 暂不支持微信头像', icon: 'none' })}>
              <Text className={styles.rowLabel}>更换头像</Text>
              <Text className={styles.rowArrow}>→</Text>
            </View>
          )}
          <View className={styles.row} onClick={handleClearCache}>
            <Text className={styles.rowLabel}>清除缓存</Text>
            <Text className={styles.rowArrow}>→</Text>
          </View>
          <View className={styles.row} onClick={handleLogout}>
            <Text className={`${styles.rowLabel} ${styles.rowDanger}`}>退出登录</Text>
          </View>
        </View>

        <View className={styles.about}>
          <Text className={styles.appName}>智学 AI</Text>
          <Text className={styles.appVersion}>v1.0.0</Text>
        </View>
      </ScrollView>
    );
  }

  return (
    <ScrollView className={styles.page} scrollY>
      <View className={styles.navBar} onClick={() => Taro.navigateBack()}>
        <Text className={styles.navBack}>← 返回</Text>
      </View>

      <View className={styles.card}>
        <View className={styles.field}>
          <Text className={styles.label}>昵称</Text>
          <Input
            className={styles.input}
            value={nickname}
            onInput={(e) => setUser({ nickname: e.detail.value })}
            placeholder="请输入昵称"
          />
        </View>
        <View className={styles.field}>
          <Text className={styles.label}>年级</Text>
          <Picker
            mode="selector"
            range={GRADES}
            value={GRADES.indexOf(grade) >= 0 ? GRADES.indexOf(grade) : 0}
            onChange={(e) => setUser({ grade: GRADES[Number(e.detail.value)] })}
          >
            <View className={styles.value}>{grade}</View>
          </Picker>
        </View>
        <View className={styles.field}>
          <Text className={styles.label}>专业</Text>
          <Picker
            mode="selector"
            range={MAJORS}
            value={MAJORS.indexOf(major) >= 0 ? MAJORS.indexOf(major) : 0}
            onChange={(e) => setUser({ major: MAJORS[Number(e.detail.value)] })}
          >
            <View className={styles.value}>{major}</View>
          </Picker>
        </View>
        <View className={styles.field}>
          <Text className={styles.label}>目标方向</Text>
          <Picker
            mode="selector"
            range={DIRECTIONS}
            value={DIRECTIONS.indexOf(targetDirection) >= 0 ? DIRECTIONS.indexOf(targetDirection) : 0}
            onChange={(e) => setUser({ targetDirection: DIRECTIONS[Number(e.detail.value)] })}
          >
            <View className={styles.value}>{targetDirection}</View>
          </Picker>
        </View>
      </View>

      <View className={styles.row} onClick={handleSave}>
        <Text className={`${styles.rowLabel} ${styles.rowDanger}`} style={{ textAlign: 'center' }}>保存</Text>
      </View>
    </ScrollView>
  );
};

export default SettingsPage;
