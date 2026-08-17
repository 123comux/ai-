import React, { useEffect, useRef, useState } from 'react';
import { View, Text, Image, ScrollView, Button, Input } from '@tarojs/components';
import Taro, { useDidShow } from '@tarojs/taro';
import RadarChart from '@/components/RadarChart';
import { useUserStore } from '@/store/useUserStore';
import { fetchAbilityReport, fetchLearningStats, fetchMenuItems, uploadAvatar, needsAvatarUpload } from '@/services/api';
import type { MenuItem } from '@/services/api';
import styles from './index.module.scss';

// 微信"头像昵称填写能力"（基础库 2.21.2+）仅在小程序端可用；H5 降级为普通昵称输入
const IS_WEAPP = process.env.TARO_ENV === 'weapp';
// 未获取到真实资料时的占位昵称（后端新用户默认值）
const PLACEHOLDER_NICKNAME = '微信用户';

const MinePage: React.FC = () => {
  const { isLoggedIn, nickname, avatar, login, logout, updateProfile } = useUserStore();
  const [abilityReport, setAbilityReport] = useState<any>(null);
  const [stats, setStats] = useState({ learningDays: 0, totalMinutes: 0, completedProjects: 0, completedLessons: 0 });
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  // 完善资料面板：微信头像昵称填写能力
  const [showProfile, setShowProfile] = useState(false);
  const [editNickname, setEditNickname] = useState('');
  const [editAvatar, setEditAvatar] = useState('');

  const loadData = async () => {
    try {
      const [reportData, statsData, menuData] = await Promise.all([
        fetchAbilityReport(),
        fetchLearningStats(),
        fetchMenuItems('mine'),
      ]);
      setAbilityReport(reportData);
      setStats(statsData);
      setMenuItems(menuData);
    } catch (err) {
      console.error('[Mine] load data error:', err);
    }
  };

  const firstShow = useRef(true);

  useEffect(() => {
    loadData();
  }, []);

  // 每次显示刷新，学习时长/能力报告同步；首次由 useEffect 承担，避免重复请求
  useDidShow(() => {
    if (firstShow.current) { firstShow.current = false; return; }
    loadData();
  });

  const handleWechatLogin = async () => {
    Taro.showLoading({ title: '微信登录中...', mask: true });
    try {
      await login();
      Taro.hideLoading();
      if (useUserStore.getState().isLoggedIn) {
        Taro.showToast({ title: '微信登录成功', icon: 'success' });
        // 首次登录拿不到真实头像昵称（微信要求用户主动授权），资料为占位时引导完善
        const state = useUserStore.getState();
        if (!state.avatar || !state.nickname || state.nickname === PLACEHOLDER_NICKNAME) {
          setEditNickname(state.nickname === PLACEHOLDER_NICKNAME ? '' : state.nickname);
          setEditAvatar(state.avatar);
          setShowProfile(true);
        }
      } else {
        Taro.showToast({ title: '登录失败，请重试', icon: 'none' });
      }
      loadData();
    } catch (err) {
      Taro.hideLoading();
      Taro.showToast({ title: err?.message || '登录失败，请重试', icon: 'none' });
    }
  };

  // 打开完善资料面板（未授权或想更换资料时）
  const openProfile = () => {
    setEditNickname(nickname === PLACEHOLDER_NICKNAME ? '' : nickname);
    setEditAvatar(avatar);
    setShowProfile(true);
  };

  // chooseAvatar 回调：用户主动选择微信头像，e.detail.avatarUrl 为临时路径（生产需上传到自有 CDN 再回传）
  const onChooseAvatar = (e: any) => {
    const url = e?.detail?.avatarUrl || '';
    if (url) setEditAvatar(url);
  };

  const handleSaveProfile = async () => {
    if (!editNickname.trim()) { Taro.showToast({ title: '请输入昵称', icon: 'none' }); return; }
    try {
      Taro.showLoading({ title: '保存中...', mask: true });
      // 微信原生头像/本地路径是会过期的临时地址，必须先上传换持久 URL 再落库；
      // 已是后端 /static/avatars 持久地址的（复用已保存头像）直接透传
      let finalAvatar = editAvatar;
      if (needsAvatarUpload(finalAvatar)) {
        finalAvatar = await uploadAvatar(finalAvatar);
      }
      await updateProfile({ nickname: editNickname.trim(), avatar: finalAvatar });
      Taro.hideLoading();
      setShowProfile(false);
      Taro.showToast({ title: '资料已更新', icon: 'success' });
      loadData();
    } catch (err: any) {
      Taro.hideLoading();
      Taro.showToast({ title: err?.message || '保存失败，请重试', icon: 'none' });
    }
  };

  const handleLogout = () => {
    Taro.showModal({
      title: '退出登录',
      content: '退出后将清除本地登录信息且无法保存学习记录，确定退出吗？',
      confirmColor: '#e5484d',
      success: (res) => {
        if (res.confirm) {
          logout();
          // 清空页面已加载的后端数据，恢复未登录初始态
          setAbilityReport(null);
          setStats({ learningDays: 0, totalMinutes: 0, completedProjects: 0, completedLessons: 0 });
          setMenuItems([]);
          Taro.showToast({ title: '已退出登录', icon: 'none' });
        }
      },
    });
  };

  const handleMenuClick = (item: MenuItem) => {
    if (item.path) {
      Taro.navigateTo({ url: item.path });
    } else {
      Taro.showToast({ title: '功能开发中', icon: 'none' });
    }
  };

  return (
    <ScrollView className={styles.page} scrollY>
      {/* 用户信息头部（微信快捷登录） */}
      <View className={styles.header}>
        <View className={styles.headerBg} />
        {isLoggedIn ? (
          <View className={styles.userInfo}>
            {/* 点头像/昵称可进入完善资料面板（微信头像昵称填写能力） */}
            <View className={styles.avatarWrap} onClick={openProfile}>
              {avatar ? (
                <Image className={styles.avatar} src={avatar} mode="aspectFill" />
              ) : (
                <View className={styles.avatarPlaceholder}><Text className={styles.avatarPlaceholderIcon}>👤</Text></View>
              )}
              <View className={styles.wechatBadge}><Text className={styles.wechatBadgeText}>微信</Text></View>
            </View>
            <Text className={styles.nickname} onClick={openProfile}>{nickname || '未设置昵称'}</Text>
            {/* 资料仍是占位时，引导用户授权真实头像昵称 */}
            {(!avatar || !nickname || nickname === PLACEHOLDER_NICKNAME) && (
              <View className={styles.editProfileHint} onClick={openProfile}>
                <Text className={styles.editProfileHintText}>完善资料，显示真实头像昵称 →</Text>
              </View>
            )}
            <View className={styles.directionBadge}>
              <Text className={styles.directionText}>微信快捷登录 · 学习记录已同步</Text>
            </View>
            <View className={styles.logoutBtn} onClick={handleLogout}>
              <Text className={styles.logoutText}>退出登录</Text>
            </View>
          </View>
        ) : (
          <View className={styles.loginEntry} onClick={handleWechatLogin}>
            <Text className={styles.loginEntryIcon}>💬</Text>
            <View className={styles.loginEntryText}>
              <Text className={styles.loginEntryTitle}>微信快捷登录</Text>
              <Text className={styles.loginEntryDesc}>一键登录，保存你的学习记录与能力档案</Text>
            </View>
            <Text className={styles.loginEntryArrow}>→</Text>
          </View>
        )}
      </View>

      {/* 学习统计 */}
      <View className={styles.statsRow}>
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{stats.learningDays}</Text>
          <Text className={styles.statLabel}>学习天数</Text>
        </View>
        <View className={styles.statDivider} />
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{stats.totalMinutes}</Text>
          <Text className={styles.statLabel}>学习时长(min)</Text>
        </View>
        <View className={styles.statDivider} />
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{stats.completedLessons}</Text>
          <Text className={styles.statLabel}>完成课程</Text>
        </View>
        <View className={styles.statDivider} />
        <View className={styles.statItem}>
          <Text className={styles.statValue}>{stats.completedProjects}</Text>
          <Text className={styles.statLabel}>完成项目</Text>
        </View>
      </View>

      {/* 押金式培训入口 */}
      <View className={styles.depositEntry} onClick={() => Taro.navigateTo({ url: '/pages/deposit/index' })}>
        <View className={styles.depositEntryLeft}>
          <Text className={styles.depositEntryTitle}>押金式培训 · 退费进度</Text>
          <Text className={styles.depositEntryDesc}>先收培训费，达标全额退，学会不花钱</Text>
        </View>
        <Text className={styles.depositEntryArrow}>→</Text>
      </View>

      {/* 学习激励入口 */}
      <View className={styles.depositEntry} onClick={() => Taro.navigateTo({ url: '/pages/community/index' })}>
        <View className={styles.depositEntryLeft}>
          <Text className={styles.depositEntryTitle}>学习激励 · 打卡/排行/社区</Text>
          <Text className={styles.depositEntryDesc}>每日打卡领模板，排行榜比拼，社区互助答疑</Text>
        </View>
        <Text className={styles.depositEntryArrow}>→</Text>
      </View>

      {/* 学习工具入口 */}
      <View className={styles.depositEntry} onClick={() => Taro.navigateTo({ url: '/pages/learningTool/index' })}>
        <View className={styles.depositEntryLeft}>
          <Text className={styles.depositEntryTitle}>学习工具 · 模板/实操/成长</Text>
          <Text className={styles.depositEntryDesc}>提示词模板库，AI 实操练习台，能力成长曲线</Text>
        </View>
        <Text className={styles.depositEntryArrow}>→</Text>
      </View>

      {/* 能力报告 */}
      {abilityReport && (
        <View className={styles.section}>
          <View className={styles.sectionHeader}>
            <Text className={styles.sectionTitle}>能力报告</Text>
            <Text className={styles.sectionMore} onClick={() => Taro.navigateTo({ url: '/pages/assessment/index' })}>
              查看详情 →
            </Text>
          </View>
          <View className={styles.reportCard}>
            <RadarChart dimensions={abilityReport.dimensions} size={400} />
            <View className={styles.reportInfo}>
              <View className={styles.reportRow}>
                <Text className={styles.reportLabel}>综合评分</Text>
                <Text className={styles.reportValue}>{abilityReport.overallScore} 分</Text>
              </View>
              <View className={styles.reportRow}>
                <Text className={styles.reportLabel}>当前水平</Text>
                <Text className={styles.reportValue}>{abilityReport.level}</Text>
              </View>
              <View className={styles.reportRow}>
                <Text className={styles.reportLabel}>推荐方向</Text>
                <Text className={styles.reportValueHighlight}>{abilityReport.recommendedDirection}</Text>
              </View>
            </View>
          </View>
        </View>
      )}

      {/* 功能菜单 */}
      <View className={styles.menuSection}>
        {menuItems.map((item, index) => (
          <View
            key={index}
            className={styles.menuItem}
            onClick={() => handleMenuClick(item)}
          >
            <Text className={styles.menuIcon}>{item.icon}</Text>
            <Text className={styles.menuLabel}>{item.label}</Text>
            <Text className={styles.menuArrow}>→</Text>
          </View>
        ))}
      </View>

      {/* 完善资料面板：微信"头像昵称填写能力"（open-type=chooseAvatar + input type=nickname） */}
      {showProfile && (
        <>
          <View className={styles.mask} onClick={() => setShowProfile(false)} />
          <View className={styles.sheet}>
            <Text className={styles.sheetTitle}>完善个人资料</Text>
            <Text className={styles.sheetDesc}>头像与昵称由你主动选择，微信不会静默获取</Text>

            <View className={styles.avatarPickerWrap}>
              {IS_WEAPP ? (
                <Button
                  className={styles.avatarPicker}
                  openType="chooseAvatar"
                  onChooseAvatar={onChooseAvatar}
                >
                  {editAvatar ? (
                    <Image className={styles.avatarPickerImage} src={editAvatar} mode="aspectFill" />
                  ) : (
                    <View className={styles.avatarPickerPlaceholder}>
                      <Text className={styles.avatarPickerPlus}>📷</Text>
                    </View>
                  )}
                </Button>
              ) : (
                <View className={styles.avatarPickerPlaceholder}>
                  <Text className={styles.avatarPickerPlus}>👤</Text>
                </View>
              )}
              <Text className={styles.avatarPickerLabel}>{IS_WEAPP ? '点击选择微信头像' : 'H5 暂不支持微信头像'}</Text>
            </View>

            <Input
              className={styles.input}
              type="nickname"
              placeholder="请输入昵称（可自动带出微信昵称）"
              value={editNickname}
              onInput={(e) => setEditNickname(e.detail.value)}
            />

            <View className={styles.sheetActions}>
              <View className={styles.btnCancel} onClick={() => setShowProfile(false)}>
                <Text className={styles.btnCancelText}>取消</Text>
              </View>
              <View className={styles.btnSave} onClick={handleSaveProfile}>
                <Text className={styles.btnSaveText}>保存</Text>
              </View>
            </View>
          </View>
        </>
      )}
    </ScrollView>
  );
};

export default MinePage;