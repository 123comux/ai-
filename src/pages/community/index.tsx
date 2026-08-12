import React, { useEffect, useRef, useState } from 'react';
import { View, Text, ScrollView, Input, Textarea, Button } from '@tarojs/components';
import Taro, { useDidShow, useShareAppMessage } from '@tarojs/taro';
import {
  doCheckin, fetchCheckinStatus, fetchLeaderboard,
  fetchPosts, createPost,
  fetchMyTeams, createTeam, joinTeam, fetchTeamDetail,
} from '@/services/api';
import type { Team } from '@/services/api';
import styles from './index.module.scss';

const TABS = [
  { key: 'checkin', label: '打卡' },
  { key: 'rank', label: '排行榜' },
  { key: 'community', label: '社区' },
  { key: 'team', label: '组队' },
];

// 小程序专属：右上角转发分享（分享学习激励页，拉新裂变）
const CommunityPage: React.FC = () => {
  // 分享回调按当前选中的小组动态生成（带邀请码进组）；未选中小组时默认分享社区页
  const shareTeamRef = useRef<Team | null>(null);
  useShareAppMessage(() => {
    const t = shareTeamRef.current;
    if (t) {
      return {
        title: `加入我的「${t.name}」一起学 AI，组队打卡不掉队`,
        path: `/pages/community/index?team=${t.code}`,
      };
    }
    return { title: '一起学 AI，每日打卡领提示词模板！', path: '/pages/community/index' };
  });

  const [activeTab, setActiveTab] = useState('checkin');
  const [checkin, setCheckin] = useState<{ today_checked: boolean; streak: number; recent_dates: string[] }>({ today_checked: false, streak: 0, recent_dates: [] });
  const [ranking, setRanking] = useState<{ ranking: any[]; my_rank: number | null; my_total_minutes: number }>({ ranking: [], my_rank: null, my_total_minutes: 0 });
  const [posts, setPosts] = useState<any[]>([]);
  const [showSheet, setShowSheet] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  // 组队
  const [teams, setTeams] = useState<Team[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [createName, setCreateName] = useState('');
  const [createMax, setCreateMax] = useState('5');
  const [showJoin, setShowJoin] = useState(false);
  const [joinCode, setJoinCode] = useState('');
  const [expandedTeam, setExpandedTeam] = useState<number | null>(null);
  const [teamDetail, setTeamDetail] = useState<{ team: Team; members: any[] } | null>(null);
  const joinedByQueryRef = useRef(false);

  const loadCheckin = async () => {
    try { setCheckin(await fetchCheckinStatus()); } catch (e) { console.error('[Community] checkin', e); }
  };
  const loadRank = async () => {
    try { setRanking(await fetchLeaderboard(10)); } catch (e) { console.error('[Community] rank', e); }
  };
  const loadPosts = async () => {
    try { setPosts(await fetchPosts()); } catch (e) { console.error('[Community] posts', e); }
  };

  const loadTeams = async () => {
    try { setTeams(await fetchMyTeams()); } catch (e) { console.error('[Community] teams', e); }
  };

  const loadAll = () => { loadCheckin(); loadRank(); loadPosts(); };
  useEffect(() => { loadAll(); }, []);
  useDidShow(() => {
    loadAll();
    loadTeams();
    // 从分享卡片进入时携带 team 邀请码，自动加入
    const params = Taro.getCurrentInstance().router?.params;
    if (params?.team && !joinedByQueryRef.current) {
      joinedByQueryRef.current = true;
      handleJoinTeam(String(params.team));
    }
  });

  const handleCreateTeam = async () => {
    if (!createName.trim()) { Taro.showToast({ title: '请输入小组名称', icon: 'none' }); return; }
    try {
      const team = await createTeam(createName.trim(), Math.max(2, Math.min(10, Number(createMax) || 5)));
      setCreateName(''); setCreateMax('5'); setShowCreate(false);
      Taro.showModal({ title: '创建成功', content: `邀请码：${team.code}\n分享给好友一起组队学习`, showCancel: false });
      await loadTeams();
      setExpandedTeam(team.id);
      setTeamDetail(null);
      try { setTeamDetail(await fetchTeamDetail(team.id)); } catch (e) { console.error(e); }
    } catch (err: any) {
      Taro.showToast({ title: err?.message || '创建失败', icon: 'none' });
    }
  };

  const handleJoinTeam = async (code?: string) => {
    const c = (code ?? joinCode).trim().toUpperCase();
    if (!c) { Taro.showToast({ title: '请输入邀请码', icon: 'none' }); return; }
    try {
      await joinTeam(c);
      setJoinCode(''); setShowJoin(false);
      Taro.showToast({ title: '加入成功', icon: 'success' });
      await loadTeams();
    } catch (err: any) {
      Taro.showToast({ title: err?.message || '加入失败', icon: 'none' });
    }
  };

  const toggleTeamDetail = async (team: Team) => {
    if (expandedTeam === team.id) {
      setExpandedTeam(null); setTeamDetail(null); return;
    }
    setExpandedTeam(team.id);
    setTeamDetail(null);
    try { setTeamDetail(await fetchTeamDetail(team.id)); } catch (e) { console.error('[Community] team detail', e); }
  };

  const handleCheckin = async () => {
    try {
      const r = await doCheckin();
      setCheckin({ today_checked: true, streak: r.streak, recent_dates: [r.checkin_date] });
      Taro.showToast({ title: `打卡成功 · 连续 ${r.streak} 天`, icon: 'success' });
      loadRank();
      // 订阅消息：打卡提醒（模板未配置则静默跳过）
      try {
        const { requestSubscriptions } = await import('@/utils/subscribe');
        requestSubscriptions();
      } catch { /* 忽略订阅失败 */ }
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

        {activeTab === 'team' && (
          <View className={styles.teamSection}>
            <View className={styles.teamActions}>
              <View className={styles.teamBtn} onClick={() => setShowCreate(true)}>
                <Text className={styles.teamBtnText}>创建小组</Text>
              </View>
              <View className={`${styles.teamBtn} ${styles.teamBtnGhost}`} onClick={() => setShowJoin(true)}>
                <Text className={styles.teamBtnGhostText}>加入小组</Text>
              </View>
            </View>

            {teams.length === 0 ? (
              <View className={styles.empty}><Text className={styles.emptyText}>还没有小组，创建或加入一个吧</Text></View>
            ) : teams.map((t) => (
              <View key={t.id} className={styles.teamCard} onClick={() => toggleTeamDetail(t)}>
                <View className={styles.teamCardHeader}>
                  <Text className={styles.teamName}>{t.name}</Text>
                  <Text className={styles.teamCount}>{t.member_count}/{t.max_members} 人</Text>
                </View>
                <View className={styles.teamCodeRow}>
                  <Text className={styles.teamCodeLabel}>邀请码</Text>
                  <Text className={styles.teamCode}>{t.code}</Text>
                </View>
                <View className={styles.teamCardFooter}>
                  <Text className={styles.teamTime}>{t.created_at?.slice(0, 10)} 创建</Text>
                  <Button
                    className={styles.inviteBtn}
                    openType="share"
                    onClick={(e) => { e.stopPropagation(); shareTeamRef.current = t; }}
                  >
                    邀请好友
                  </Button>
                </View>
                {expandedTeam === t.id && (
                  <View className={styles.teamDetail}>
                    {!teamDetail ? (
                      <Text className={styles.teamDetailLoading}>加载成员中…</Text>
                    ) : teamDetail.members.length === 0 ? (
                      <Text className={styles.teamDetailLoading}>暂无成员</Text>
                    ) : teamDetail.members.map((m, i) => (
                      <View key={m.id} className={styles.teamMember}>
                        <Text className={styles.teamMemberRank}>{i + 1}</Text>
                        <Text className={styles.teamMemberName}>{m.nickname || '匿名用户'}</Text>
                        <Text className={styles.teamMemberMinutes}>{m.total_minutes} 分钟</Text>
                      </View>
                    ))}
                  </View>
                )}
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

      {showCreate && (
        <>
          <View className={styles.mask} onClick={() => setShowCreate(false)} />
          <View className={styles.sheet}>
            <Text className={styles.sheetTitle}>创建学习小组</Text>
            <Input className={styles.input} placeholder="小组名称" value={createName} onInput={(e) => setCreateName(e.detail.value)} />
            <Input className={styles.input} type="number" placeholder="人数上限（2-10）" value={createMax} onInput={(e) => setCreateMax(e.detail.value)} />
            <View className={styles.sheetActions}>
              <View className={styles.btnCancel} onClick={() => setShowCreate(false)}>
                <Text className={styles.btnCancelText}>取消</Text>
              </View>
              <View className={styles.btnSave} onClick={handleCreateTeam}>
                <Text className={styles.btnSaveText}>创建</Text>
              </View>
            </View>
          </View>
        </>
      )}

      {showJoin && (
        <>
          <View className={styles.mask} onClick={() => setShowJoin(false)} />
          <View className={styles.sheet}>
            <Text className={styles.sheetTitle}>加入学习小组</Text>
            <Input className={styles.input} placeholder="输入邀请码" value={joinCode} onInput={(e) => setJoinCode(e.detail.value)} />
            <View className={styles.sheetActions}>
              <View className={styles.btnCancel} onClick={() => setShowJoin(false)}>
                <Text className={styles.btnCancelText}>取消</Text>
              </View>
              <View className={styles.btnSave} onClick={() => handleJoinTeam()}>
                <Text className={styles.btnSaveText}>加入</Text>
              </View>
            </View>
          </View>
        </>
      )}
    </View>
  );
};

export default CommunityPage;
