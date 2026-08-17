import React, { useState, useCallback, useEffect } from 'react';
import { View, Text, ScrollView, Input, Picker, Button, Image } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useUserStore } from '@/store/useUserStore';
import { uploadAvatar, fetchDevConfig, fetchDevUsers, needsAvatarUpload } from '@/services/api';
import type { DevUser } from '@/services/api';
import styles from './index.module.scss';

// 预设选项：客户可从中选，也可选"自定义"自由输入（列表末尾追加自定义入口）
const GRADES = ['大一', '大二', '大三', '大四', '研究生', '已毕业'];
const MAJORS = ['计算机科学与技术', '软件工程', '人工智能', '数据科学', '电子信息', '自动化', '其他'];
// 目标方向 = 五阶段学习方向，与首页 DIRECTION_TOPIC_MAP / 课程阶段保持一致
const DIRECTIONS = ['零基础认知', '入门实践', '提示词进阶', '场景实战', '熟练精通'];
const CUSTOM_LABEL = '自定义…';

// 微信"头像昵称填写能力"（基础库 2.21.2+）仅在小程序端可用
const IS_WEAPP = process.env.TARO_ENV === 'weapp';

const SettingsPage: React.FC = () => {
  const { nickname, avatar, grade, major, targetDirection, setUser, logout, updateProfile, impersonate } = useUserStore();
  const [editing, setEditing] = useState(false);
  // 当前处于"自定义输入"的资料字段（选"自定义…"后进入手输，失焦回到选择器）
  const [customField, setCustomField] = useState<'grade' | 'major' | 'targetDirection' | null>(null);
  // 开发期模拟切换用户（后端 DEV_IMPERSONATE=true 才展示）
  const [devEnabled, setDevEnabled] = useState(false);
  const [devUsers, setDevUsers] = useState<DevUser[]>([]);

  const loadDev = useCallback(async () => {
    try {
      const cfg = await fetchDevConfig();
      if (cfg.impersonate_enabled) {
        setDevEnabled(true);
        setDevUsers(await fetchDevUsers());
      }
    } catch (e) {
      // 接口未开放（404）时静默隐藏开发区
    }
  }, []);
  useEffect(() => { loadDev(); }, [loadDev]);

  // 资料字段配置：key 即 store 字段名，value 当前值，options 预设选项
  const fields: { key: 'grade' | 'major' | 'targetDirection'; label: string; value: string; options: string[] }[] = [
    { key: 'grade', label: '年级', value: grade, options: GRADES },
    { key: 'major', label: '专业', value: major, options: MAJORS },
    { key: 'targetDirection', label: '目标方向', value: targetDirection, options: DIRECTIONS },
  ];

  const handleSave = async () => {
    try {
      setUser({ nickname, grade, major, targetDirection });
      // 资料统一存后端（昵称/头像/年级/专业/目标方向），不再写本地 user_info
      await updateProfile({ nickname, grade, major, targetDirection });
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

  // 切换账号：退出并清空本地登录态，回到登录入口；在开发者工具顶部切换模拟账号后重新登录
  const handleSwitchAccount = () => {
    Taro.showModal({
      title: '切换账号',
      content: '将退出当前账号并清除本地登录信息。测试多个账号时，请在微信开发者工具顶部切换模拟账号后重新登录。',
      confirmColor: '#e5484d',
      success: (res) => {
        if (res.confirm) {
          logout();
          Taro.showToast({ title: '已退出，请重新登录', icon: 'none' });
          setTimeout(() => Taro.navigateBack(), 600);
        }
      },
    });
  };

  // 头像选择：open-type=chooseAvatar 用户主动授权微信头像，先上传换持久 URL 再回传后端
  const handleAvatar = async (url: string) => {
    if (!url) return;
    try {
      Taro.showLoading({ title: '更新中...', mask: true });
      // 微信临时头像路径（wxfile/http://tmp）先上传换持久 URL；已是后端 /static/avatars 地址直接透传
      const finalUrl = needsAvatarUpload(url) ? await uploadAvatar(url) : url;
      await updateProfile({ nickname, avatar: finalUrl });
      Taro.hideLoading();
      Taro.showToast({ title: '头像已更新', icon: 'success' });
    } catch (err: any) {
      Taro.hideLoading();
      Taro.showToast({ title: err?.message || '更新失败', icon: 'none' });
    }
  };

  // 开发期模拟切换：以目标用户身份进入
  const handleImpersonate = (u: DevUser) => {
    const label = u.nickname || `用户${u.id}`;
    Taro.showModal({
      title: '模拟切换用户',
      content: `以「${label}」身份进入？（仅开发测试用，用于验证多用户数据隔离）`,
      success: async (res) => {
        if (!res.confirm) return;
        try {
          Taro.showLoading({ title: '切换中...', mask: true });
          await impersonate(u.id);
          Taro.hideLoading();
          Taro.showToast({ title: `已切换为 ${label}`, icon: 'success' });
        } catch (err: any) {
          Taro.hideLoading();
          Taro.showToast({ title: err?.message || '切换失败', icon: 'none' });
        }
      },
    });
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
            <Text className={styles.value}>{nickname || '未设置'}</Text>
          </View>
          <View className={styles.row}>
            <Text className={styles.rowLabel}>年级</Text>
            <Text className={styles.value}>{grade || '未填写'}</Text>
          </View>
          <View className={styles.row}>
            <Text className={styles.rowLabel}>专业</Text>
            <Text className={styles.value}>{major || '未填写'}</Text>
          </View>
          <View className={styles.row}>
            <Text className={styles.rowLabel}>目标方向</Text>
            <Text className={styles.value}>{targetDirection || '未填写'}</Text>
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
          <View className={styles.row} onClick={handleSwitchAccount}>
            <Text className={styles.rowLabel}>切换账号</Text>
            <Text className={styles.rowArrow}>→</Text>
          </View>
          <View className={styles.row} onClick={handleLogout}>
            <Text className={`${styles.rowLabel} ${styles.rowDanger}`}>退出登录</Text>
          </View>
        </View>

        {/* 开发期模拟切换用户（仅 DEV_IMPERSONATE=true 时展示） */}
        {devEnabled && (
          <View className={styles.card}>
            <View className={styles.devHeader}>
              <Text className={styles.devTitle}>开发测试 · 模拟切换用户</Text>
              <Text className={styles.devHint}>仅本地开发可见，点击以该用户身份进入</Text>
            </View>
            {devUsers.length === 0 ? (
              <View className={styles.devEmpty}><Text className={styles.devEmptyText}>暂无用户</Text></View>
            ) : devUsers.map((u) => (
              <View key={u.id} className={styles.row} onClick={() => handleImpersonate(u)}>
                <Text className={styles.devUserNick}>{u.nickname || `用户${u.id}`}</Text>
                <Text className={styles.devUserMeta}>#{u.id} · {u.openid.slice(0, 12)}…</Text>
                <Text className={styles.rowArrow}>→</Text>
              </View>
            ))}
          </View>
        )}

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
        {fields.map((f) => {
          const isCustom = customField === f.key;
          const opts = [...f.options, CUSTOM_LABEL];
          const idx = f.value ? (opts.indexOf(f.value) >= 0 ? opts.indexOf(f.value) : opts.length - 1) : 0;
          return (
            <View className={styles.field} key={f.key}>
              <Text className={styles.label}>{f.label}</Text>
              {isCustom ? (
                <Input
                  className={styles.input}
                  placeholder={`请输入${f.label}`}
                  value={f.value}
                  onInput={(e) => setUser({ [f.key]: e.detail.value } as any)}
                  onBlur={() => setCustomField(null)}
                />
              ) : (
                <Picker
                  mode="selector"
                  range={opts}
                  value={idx}
                  onChange={(e) => {
                    const i = Number(e.detail.value);
                    if (i === opts.length - 1) {
                      // 选择"自定义…"：进入手输，保留已填内容
                      setCustomField(f.key);
                    } else {
                      setCustomField(null);
                      setUser({ [f.key]: opts[i] } as any);
                    }
                  }}
                >
                  <View className={styles.value}>{f.value || '请选择'}</View>
                </Picker>
              )}
            </View>
          );
        })}
      </View>

      <View className={styles.row} onClick={handleSave}>
        <Text className={`${styles.rowLabel} ${styles.rowDanger}`} style={{ textAlign: 'center' }}>保存</Text>
      </View>
    </ScrollView>
  );
};

export default SettingsPage;
