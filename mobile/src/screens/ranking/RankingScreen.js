import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Modal,
  ScrollView
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { colors, getFactionColor } from '../../styles/colors';
import { spacing } from '../../styles/spacing';
import { fetchPlayerRankings, setRankingFilter } from '../../store/reducers/rankingReducer';
import { setRefreshing } from '../../store/reducers/uiReducer';

const FACTIONS = ['all', '梵天', '比湿奴', '湿婆'];
const TIME_RANGES = [
  { key: 'today', label: '今天' },
  { key: 'yesterday', label: '昨天' },
  { key: 'week', label: '本周' },
  { key: 'month', label: '本月' },
  { key: 'three_months', label: '三月' }
];

export default function RankingScreen({ navigation, route }) {
  const dispatch = useDispatch();
  const { players, selectedFaction, selectedJob, selectedTimeRange, isLoading } = useSelector(
    state => state.ranking
  );
  const { refreshing } = useSelector(state => state.ui);
  const [filterModalVisible, setFilterModalVisible] = useState(false);
  const [jobs, setJobs] = useState([]);

  // 从路由参数获取初始势力
  useEffect(() => {
    if (route.params?.faction) {
      dispatch(setRankingFilter(route.params.faction, null, selectedTimeRange));
    }
  }, [route.params?.faction]);

  // 加载排名数据
  useEffect(() => {
    loadRankings();
  }, [selectedFaction, selectedJob, selectedTimeRange]);

  const loadRankings = async () => {
    try {
      await dispatch(
        fetchPlayerRankings(
          selectedFaction === 'all' ? null : selectedFaction,
          selectedTimeRange,
          selectedJob
        )
      );
    } catch (error) {
      console.error('Load rankings error:', error);
    }
  };

  const onRefresh = async () => {
    dispatch(setRefreshing(true));
    try {
      await loadRankings();
    } finally {
      dispatch(setRefreshing(false));
    }
  };

  const handleFactionChange = (faction) => {
    dispatch(setRankingFilter(faction, selectedJob, selectedTimeRange));
    setFilterModalVisible(false);
  };

  const handleTimeRangeChange = (timeRange) => {
    dispatch(setRankingFilter(selectedFaction, selectedJob, timeRange));
    setFilterModalVisible(false);
  };

  const renderRankingCard = ({ item, index }) => (
    <TouchableOpacity
      style={styles.rankingCard}
      onPress={() => navigation.navigate('PlayerDetail', { playerName: item.name })}
      activeOpacity={0.7}
    >
      <View style={styles.rankingCardContent}>
        {/* 排名 */}
        <View style={styles.rankBadge}>
          <Text style={styles.rankBadgeText}>
            {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
          </Text>
        </View>

        {/* 玩家信息 */}
        <View style={styles.playerInfo}>
          <Text style={styles.playerName}>{item.name}</Text>
          <View style={styles.playerMeta}>
            <View
              style={[
                styles.factionBadge,
                { backgroundColor: `${getFactionColor(item.faction)}20` }
              ]}
            >
              <Text
                style={[
                  styles.factionBadgeText,
                  { color: getFactionColor(item.faction) }
                ]}
              >
                {item.faction}
              </Text>
            </View>
            {item.job && (
              <Text style={styles.jobText}>{item.job}</Text>
            )}
          </View>
        </View>

        {/* 统计数据 */}
        <View style={styles.statsColumn}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>击杀</Text>
            <Text style={styles.statValue}>{item.kills}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>死亡</Text>
            <Text style={styles.statValue}>{item.deaths}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>K/D</Text>
            <Text style={styles.statValue}>{item.kd_ratio}</Text>
          </View>
        </View>

        {/* 得分 */}
        <View style={styles.scoreColumn}>
          <Text style={styles.scoreLabel}>得分</Text>
          <Text style={styles.scoreValue}>{item.score}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  const renderFilterModal = () => (
    <Modal
      visible={filterModalVisible}
      transparent
      animationType="slide"
      onRequestClose={() => setFilterModalVisible(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          {/* 模态框头部 */}
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>筛选</Text>
            <TouchableOpacity onPress={() => setFilterModalVisible(false)}>
              <MaterialCommunityIcons
                name="close"
                size={24}
                color={colors.neutral[700]}
              />
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalBody} showsVerticalScrollIndicator={false}>
            {/* 势力筛选 */}
            <View style={styles.filterSection}>
              <Text style={styles.filterSectionTitle}>势力</Text>
              <View style={styles.filterOptions}>
                {FACTIONS.map(faction => (
                  <TouchableOpacity
                    key={faction}
                    style={[
                      styles.filterOption,
                      selectedFaction === faction && styles.filterOptionActive
                    ]}
                    onPress={() => handleFactionChange(faction)}
                  >
                    <Text
                      style={[
                        styles.filterOptionText,
                        selectedFaction === faction && styles.filterOptionTextActive
                      ]}
                    >
                      {faction === 'all' ? '全部' : faction}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* 时间范围筛选 */}
            <View style={styles.filterSection}>
              <Text style={styles.filterSectionTitle}>时间范围</Text>
              <View style={styles.filterOptions}>
                {TIME_RANGES.map(range => (
                  <TouchableOpacity
                    key={range.key}
                    style={[
                      styles.filterOption,
                      selectedTimeRange === range.key && styles.filterOptionActive
                    ]}
                    onPress={() => handleTimeRangeChange(range.key)}
                  >
                    <Text
                      style={[
                        styles.filterOptionText,
                        selectedTimeRange === range.key && styles.filterOptionTextActive
                      ]}
                    >
                      {range.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </ScrollView>
        </View>
      </View>
    </Modal>
  );

  return (
    <View style={styles.container}>
      {/* 顶部栏 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>排名</Text>
        <TouchableOpacity
          style={styles.filterButton}
          onPress={() => setFilterModalVisible(true)}
        >
          <MaterialCommunityIcons
            name="filter"
            size={24}
            color={colors.primary}
          />
        </TouchableOpacity>
      </View>

      {/* 活跃筛选器显示 */}
      <View style={styles.activeFilters}>
        <View style={styles.filterTag}>
          <Text style={styles.filterTagText}>
            {selectedFaction === 'all' ? '全部' : selectedFaction}
          </Text>
        </View>
        <View style={styles.filterTag}>
          <Text style={styles.filterTagText}>
            {TIME_RANGES.find(r => r.key === selectedTimeRange)?.label}
          </Text>
        </View>
      </View>

      {/* 排名列表 */}
      {isLoading && players.length === 0 ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : (
        <FlatList
          data={players}
          renderItem={renderRankingCard}
          keyExtractor={(item, index) => `${item.id}-${index}`}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={colors.primary}
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <MaterialCommunityIcons
                name="inbox"
                size={48}
                color={colors.neutral[300]}
              />
              <Text style={styles.emptyText}>暂无数据</Text>
            </View>
          }
          showsVerticalScrollIndicator={false}
        />
      )}

      {/* 筛选模态框 */}
      {renderFilterModal()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
    backgroundColor: colors.background,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.neutral[900]
  },
  filterButton: {
    padding: spacing.md
  },
  activeFilters: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface
  },
  filterTag: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20,
    marginRight: spacing.md
  },
  filterTagText: {
    fontSize: 12,
    fontWeight: '500',
    color: colors.background
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  listContent: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg
  },
  rankingCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    marginBottom: spacing.md,
    overflow: 'hidden'
  },
  rankingCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.lg
  },
  rankBadge: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.lg
  },
  rankBadgeText: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.background
  },
  playerInfo: {
    flex: 1
  },
  playerName: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.neutral[900],
    marginBottom: spacing.sm
  },
  playerMeta: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  factionBadge: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 6,
    marginRight: spacing.md
  },
  factionBadgeText: {
    fontSize: 11,
    fontWeight: '600'
  },
  jobText: {
    fontSize: 11,
    color: colors.neutral[500]
  },
  statsColumn: {
    flexDirection: 'row',
    marginRight: spacing.lg
  },
  statItem: {
    alignItems: 'center',
    marginRight: spacing.lg
  },
  statLabel: {
    fontSize: 10,
    color: colors.neutral[500],
    marginBottom: spacing.sm
  },
  statValue: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.neutral[900]
  },
  scoreColumn: {
    alignItems: 'flex-end'
  },
  scoreLabel: {
    fontSize: 10,
    color: colors.neutral[500],
    marginBottom: spacing.sm
  },
  scoreValue: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.primary
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: spacing.xxxl
  },
  emptyText: {
    fontSize: 14,
    color: colors.neutral[400],
    marginTop: spacing.md
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end'
  },
  modalContent: {
    backgroundColor: colors.background,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%'
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.neutral[900]
  },
  modalBody: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg
  },
  filterSection: {
    marginBottom: spacing.xl
  },
  filterSectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.neutral[900],
    marginBottom: spacing.md
  },
  filterOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap'
  },
  filterOption: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    marginRight: spacing.md,
    marginBottom: spacing.md
  },
  filterOptionActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary
  },
  filterOptionText: {
    fontSize: 12,
    fontWeight: '500',
    color: colors.neutral[600]
  },
  filterOptionTextActive: {
    color: colors.background
  }
});
