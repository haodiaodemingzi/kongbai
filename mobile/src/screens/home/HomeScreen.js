import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Dimensions,
  TouchableOpacity,
  ActivityIndicator
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { BarChart, LineChart } from 'react-native-chart-kit';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { colors, getFactionColor } from '../../styles/colors';
import { spacing } from '../../styles/spacing';
import { rankingService } from '../../services/ranking';
import { fetchFactionStats } from '../../store/reducers/rankingReducer';
import { setRefreshing } from '../../store/reducers/uiReducer';

const screenWidth = Dimensions.get('window').width;

export default function HomeScreen({ navigation }) {
  const dispatch = useDispatch();
  const { factionStats } = useSelector(state => state.ranking);
  const { refreshing } = useSelector(state => state.ui);
  const [dateRange, setDateRange] = useState('week');
  const [dailyData, setDailyData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [dateRange]);

  const loadData = async () => {
    setLoading(true);
    try {
      await dispatch(fetchFactionStats(dateRange));
      
      // 获取每日数据
      const kills = await rankingService.getDailyKills(dateRange, 5);
      setDailyData(kills);
    } catch (error) {
      console.error('Load data error:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    dispatch(setRefreshing(true));
    try {
      await loadData();
    } finally {
      dispatch(setRefreshing(false));
    }
  };

  const renderStatCard = (title, value, icon, color) => (
    <View style={[styles.statCard, { borderLeftColor: color }]}>
      <View style={styles.statCardContent}>
        <View style={styles.statCardLeft}>
          <Text style={styles.statCardTitle}>{title}</Text>
          <Text style={styles.statCardValue}>{value.toLocaleString()}</Text>
        </View>
        <View style={[styles.statCardIcon, { backgroundColor: `${color}20` }]}>
          <MaterialCommunityIcons name={icon} size={24} color={color} />
        </View>
      </View>
    </View>
  );

  const renderFactionChart = () => {
    if (!factionStats || factionStats.length === 0) {
      return null;
    }

    const chartData = {
      labels: factionStats.map(([faction]) => faction.substring(0, 2)),
      datasets: [
        {
          data: factionStats.map(([, stats]) => stats.total_kills),
          color: (opacity = 1) => `rgba(37, 99, 235, ${opacity})`
        }
      ]
    };

    return (
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>势力击杀对比</Text>
        <BarChart
          data={chartData}
          width={screenWidth - spacing.lg * 2}
          height={220}
          chartConfig={{
            backgroundColor: colors.background,
            backgroundGradientFrom: colors.background,
            backgroundGradientTo: colors.background,
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(37, 99, 235, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(107, 114, 128, ${opacity})`,
            style: {
              borderRadius: 12
            },
            propsForBackLabel: {
              fontSize: 12
            }
          }}
          style={styles.chart}
        />
      </View>
    );
  };

  const renderDailyChart = () => {
    if (!dailyData || dailyData.dates.length === 0) {
      return null;
    }

    const chartData = {
      labels: dailyData.dates.map(date => {
        const d = new Date(date);
        return `${d.getMonth() + 1}/${d.getDate()}`;
      }),
      datasets: dailyData.players.slice(0, 1).map(player => ({
        data: player.data,
        color: (opacity = 1) => `rgba(37, 99, 235, ${opacity})`
      }))
    };

    return (
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>每日击杀趋势</Text>
        <LineChart
          data={chartData}
          width={screenWidth - spacing.lg * 2}
          height={220}
          chartConfig={{
            backgroundColor: colors.background,
            backgroundGradientFrom: colors.background,
            backgroundGradientTo: colors.background,
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(37, 99, 235, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(107, 114, 128, ${opacity})`,
            style: {
              borderRadius: 12
            }
          }}
          style={styles.chart}
        />
      </View>
    );
  };

  const renderFactionCards = () => {
    if (!factionStats || factionStats.length === 0) {
      return null;
    }

    return (
      <View style={styles.factionCardsContainer}>
        <Text style={styles.sectionTitle}>势力统计</Text>
        {factionStats.map(([faction, stats]) => (
          <TouchableOpacity
            key={faction}
            style={[
              styles.factionCard,
              { borderLeftColor: getFactionColor(faction) }
            ]}
            onPress={() => navigation.navigate('Ranking', { faction })}
          >
            <View style={styles.factionCardHeader}>
              <Text style={styles.factionName}>{faction}</Text>
              <View style={styles.factionBadge}>
                <Text style={styles.factionBadgeText}>
                  {stats.player_count} 人
                </Text>
              </View>
            </View>
            <View style={styles.factionStats}>
              <View style={styles.factionStatItem}>
                <Text style={styles.factionStatLabel}>击杀</Text>
                <Text style={styles.factionStatValue}>
                  {stats.total_kills}
                </Text>
              </View>
              <View style={styles.factionStatItem}>
                <Text style={styles.factionStatLabel}>死亡</Text>
                <Text style={styles.factionStatValue}>
                  {stats.total_deaths}
                </Text>
              </View>
              <View style={styles.factionStatItem}>
                <Text style={styles.factionStatLabel}>祝福</Text>
                <Text style={styles.factionStatValue}>
                  {stats.total_blessings}
                </Text>
              </View>
            </View>
            {stats.top_killer && (
              <View style={styles.factionTopPlayer}>
                <Text style={styles.factionTopPlayerLabel}>
                  🔥 {stats.top_killer.name} ({stats.top_killer.kills} 击杀)
                </Text>
              </View>
            )}
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  const renderTopScorers = () => {
    if (!factionStats || factionStats.length === 0) {
      return null;
    }

    const topScorers = factionStats
      .filter(([, stats]) => stats.top_scorer)
      .map(([faction, stats]) => ({
        ...stats.top_scorer,
        faction
      }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 5);

    if (topScorers.length === 0) {
      return null;
    }

    return (
      <View style={styles.topScorersContainer}>
        <Text style={styles.sectionTitle}>得分榜 Top 5</Text>
        {topScorers.map((player, index) => (
          <TouchableOpacity
            key={index}
            style={styles.topScorerItem}
            onPress={() => navigation.navigate('Ranking', { faction: player.faction })}
          >
            <View style={styles.topScorerRank}>
              <Text style={styles.topScorerRankText}>
                {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
              </Text>
            </View>
            <View style={styles.topScorerInfo}>
              <Text style={styles.topScorerName}>{player.name}</Text>
              <Text style={styles.topScorerFaction}>{player.faction}</Text>
            </View>
            <Text style={styles.topScorerScore}>{player.score}</Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  if (loading && !factionStats) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* 顶部栏 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>首页</Text>
        <TouchableOpacity onPress={() => navigation.navigate('Profile')}>
          <MaterialCommunityIcons
            name="cog"
            size={24}
            color={colors.neutral[700]}
          />
        </TouchableOpacity>
      </View>

      {/* 时间范围选择 */}
      <View style={styles.dateRangeContainer}>
        {['today', 'week', 'month', 'three_months'].map(range => (
          <TouchableOpacity
            key={range}
            style={[
              styles.dateRangeButton,
              dateRange === range && styles.dateRangeButtonActive
            ]}
            onPress={() => setDateRange(range)}
          >
            <Text
              style={[
                styles.dateRangeButtonText,
                dateRange === range && styles.dateRangeButtonTextActive
              ]}
            >
              {range === 'today' ? '今天' : range === 'week' ? '本周' : range === 'month' ? '本月' : '三月'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* 内容 */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={colors.primary}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* 统计卡片 */}
        <View style={styles.statsContainer}>
          {factionStats && factionStats.length > 0 && (
            <>
              {renderStatCard(
                '总击杀',
                factionStats.reduce((sum, [, stats]) => sum + stats.total_kills, 0),
                'sword',
                colors.primary
              )}
              {renderStatCard(
                '总死亡',
                factionStats.reduce((sum, [, stats]) => sum + stats.total_deaths, 0),
                'skull',
                colors.error
              )}
              {renderStatCard(
                '总得分',
                factionStats.reduce((sum, [, stats]) => sum + (stats.top_scorer?.score || 0), 0),
                'star',
                colors.warning
              )}
            </>
          )}
        </View>

        {/* 图表 */}
        {renderFactionChart()}
        {renderDailyChart()}

        {/* 势力统计 */}
        {renderFactionCards()}

        {/* 得分榜 */}
        {renderTopScorers()}

        <View style={styles.bottomPadding} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
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
  dateRangeContainer: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  dateRangeButton: {
    flex: 1,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    marginHorizontal: spacing.sm / 2,
    borderRadius: 8,
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center'
  },
  dateRangeButtonActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary
  },
  dateRangeButtonText: {
    fontSize: 12,
    fontWeight: '500',
    color: colors.neutral[600]
  },
  dateRangeButtonTextActive: {
    color: colors.background
  },
  content: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg
  },
  statsContainer: {
    marginBottom: spacing.xl
  },
  statCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
    borderLeftWidth: 4,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  statCardContent: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  statCardLeft: {
    flex: 1
  },
  statCardTitle: {
    fontSize: 12,
    color: colors.neutral[500],
    marginBottom: spacing.sm
  },
  statCardValue: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.neutral[900]
  },
  statCardIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center'
  },
  chartContainer: {
    marginBottom: spacing.xl
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.neutral[900],
    marginBottom: spacing.md
  },
  chart: {
    borderRadius: 12,
    marginVertical: spacing.md
  },
  factionCardsContainer: {
    marginBottom: spacing.xl
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.neutral[900],
    marginBottom: spacing.lg
  },
  factionCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
    borderLeftWidth: 4
  },
  factionCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md
  },
  factionName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.neutral[900]
  },
  factionBadge: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20
  },
  factionBadgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.background
  },
  factionStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: spacing.md,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  factionStatItem: {
    alignItems: 'center'
  },
  factionStatLabel: {
    fontSize: 12,
    color: colors.neutral[500],
    marginBottom: spacing.sm
  },
  factionStatValue: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.neutral[900]
  },
  factionTopPlayer: {
    backgroundColor: `${colors.primary}10`,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 8
  },
  factionTopPlayerLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: colors.primary
  },
  topScorersContainer: {
    marginBottom: spacing.xl
  },
  topScorerItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md
  },
  topScorerRank: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.lg
  },
  topScorerRankText: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.background
  },
  topScorerInfo: {
    flex: 1
  },
  topScorerName: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.neutral[900],
    marginBottom: spacing.sm
  },
  topScorerFaction: {
    fontSize: 12,
    color: colors.neutral[500]
  },
  topScorerScore: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.primary
  },
  bottomPadding: {
    height: spacing.xl
  }
});
