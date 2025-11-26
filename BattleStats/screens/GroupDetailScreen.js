import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { getGroupKillDetails, getGroupDetails } from '../services/api';
import { useTheme } from '../contexts/ThemeContext';

export default function GroupDetailScreen({ groupName, timeRange, onBack }) {
  const { colors } = useTheme();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('kills'); // 'kills' 或 'members'
  const [killDetails, setKillDetails] = useState([]);
  const [deathDetails, setDeathDetails] = useState([]);
  const [members, setMembers] = useState([]);

  useEffect(() => {
    fetchGroupDetails();
  }, [activeTab]);

  const fetchGroupDetails = async () => {
    try {
      setLoading(true);
      
      console.log('=== GroupDetailScreen fetchGroupDetails ===');
      console.log('groupName:', groupName);
      console.log('activeTab:', activeTab);
      console.log('timeRange:', timeRange);
      
      if (activeTab === 'kills') {
        // 获取击杀数据
        const params = {
          group_name: groupName,
          direction: 'out',
        };
        
        if (timeRange && timeRange.startDate && timeRange.endDate) {
          params.start_datetime = timeRange.startDate;
          params.end_datetime = timeRange.endDate;
        }
        
        console.log('击杀数据请求参数:', params);
        const result = await getGroupKillDetails(params);
        
        if (result.success) {
          setKillDetails(result.data.details || []);
        } else {
          Alert.alert('错误', result.message || '获取分组击杀明细失败');
        }

        // 获取被杀明细
        const deathParams = {
          group_name: groupName,
          direction: 'in',
        };
        
        if (timeRange && timeRange.startDate && timeRange.endDate) {
          deathParams.start_datetime = timeRange.startDate;
          deathParams.end_datetime = timeRange.endDate;
        }

        const deathResult = await getGroupKillDetails(deathParams);
        
        if (deathResult.success) {
          setDeathDetails(deathResult.data.details || []);
        }
      } else {
        // 获取成员战绩
        const params = {
          player_name: groupName,
        };
        
        if (timeRange && timeRange.startDate && timeRange.endDate) {
          params.start_datetime = timeRange.startDate;
          params.end_datetime = timeRange.endDate;
        }
        
        console.log('成员战绩请求参数:', params);
        const result = await getGroupDetails(params);
        console.log('成员战绩返回结果:', result);
        
        if (result.success) {
          setMembers(result.data.members || []);
        } else {
          Alert.alert('错误', result.message || '获取分组成员失败');
        }
      }
    } catch (error) {
      console.error('获取分组详情失败:', error);
      Alert.alert('错误', '获取分组详情失败');
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  };

  const renderTabContent = () => {
    if (loading) {
      return (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={[styles.loadingText, { color: colors.textSecondary }]}>加载中...</Text>
        </View>
      );
    }

    if (activeTab === 'kills') {
      return (
        <>
          {/* 击杀明细 */}
          <View style={styles.detailsSection}>
            <Text style={[styles.sectionTitle, { color: colors.text }]}>击杀明细</Text>
            {killDetails && killDetails.length > 0 ? (
              killDetails.map((kill, index) => (
                <View key={kill.id || index} style={[styles.detailCard, { backgroundColor: colors.cardBackground }]}>
                  <View style={styles.detailHeader}>
                    <Text style={[styles.detailName, { color: colors.text }]}>{kill.name}</Text>
                    <Text style={[styles.detailCount, styles.killCount]}>{kill.count}次</Text>
                  </View>
                  <View style={styles.detailInfo}>
                    <Text style={[styles.detailLabel, { color: colors.textSecondary }]}>职业：</Text>
                    <Text style={[styles.detailValue, { color: colors.text }]}>{kill.job}</Text>
                  </View>
                  <View style={styles.detailInfo}>
                    <Text style={[styles.detailLabel, { color: colors.textSecondary }]}>势力：</Text>
                    <Text style={[styles.detailValue, { color: colors.text }]}>{kill.god}</Text>
                  </View>
                </View>
              ))
            ) : (
              <Text style={[styles.noDataText, { color: colors.textSecondary }]}>暂无击杀记录</Text>
            )}
          </View>

          {/* 被杀明细 */}
          <View style={styles.detailsSection}>
            <Text style={[styles.sectionTitle, { color: colors.text }]}>被杀明细</Text>
            {deathDetails && deathDetails.length > 0 ? (
              deathDetails.map((death, index) => (
                <View key={death.id || index} style={[styles.detailCard, { backgroundColor: colors.cardBackground }]}>
                  <View style={styles.detailHeader}>
                    <Text style={[styles.detailName, { color: colors.text }]}>{death.name}</Text>
                    <Text style={[styles.detailCount, styles.deathCount]}>{death.count}次</Text>
                  </View>
                  <View style={styles.detailInfo}>
                    <Text style={[styles.detailLabel, { color: colors.textSecondary }]}>职业：</Text>
                    <Text style={[styles.detailValue, { color: colors.text }]}>{death.job}</Text>
                  </View>
                  <View style={styles.detailInfo}>
                    <Text style={[styles.detailLabel, { color: colors.textSecondary }]}>势力：</Text>
                    <Text style={[styles.detailValue, { color: colors.text }]}>{death.god}</Text>
                  </View>
                </View>
              ))
            ) : (
              <Text style={[styles.noDataText, { color: colors.textSecondary }]}>暂无被杀记录</Text>
            )}
          </View>
        </>
      );
    } else {
      return (
        <View style={styles.membersSection}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>成员战绩</Text>
          {/* 表头 */}
          <View style={[styles.tableHeader, { backgroundColor: colors.cardBackground, borderBottomColor: colors.border }]}>
            <Text style={[styles.tableHeaderText, { flex: 2, color: colors.text }]}>游戏ID</Text>
            <Text style={[styles.tableHeaderText, { flex: 1, color: colors.text }]}>职业</Text>
            <Text style={[styles.tableHeaderText, { flex: 1, color: colors.text }]}>势力</Text>
            <Text style={[styles.tableHeaderText, { flex: 1, color: colors.text }]}>击杀</Text>
            <Text style={[styles.tableHeaderText, { flex: 1, color: colors.text }]}>死亡</Text>
            <Text style={[styles.tableHeaderText, { flex: 1, color: colors.text }]}>爆灯</Text>
          </View>

          {/* 成员数据 */}
          {members && members.length > 0 ? (
            members.map((member, index) => (
              <View
                key={member.id || index}
                style={[
                  styles.memberRow,
                  { 
                    backgroundColor: index % 2 === 0 ? colors.cardBackground : colors.background,
                    borderBottomColor: colors.border 
                  }
                ]}
              >
                <Text style={[styles.memberName, { color: colors.text }]} numberOfLines={1}>
                  {member.name}
                </Text>
                <Text style={[styles.memberText, { color: colors.textSecondary }]}>
                  {member.job}
                </Text>
                <Text style={[styles.memberText, { color: colors.textSecondary }]}>
                  {member.god}
                </Text>
                <Text style={[styles.memberStat, { color: colors.primary }]}>
                  {member.kills}
                </Text>
                <Text style={[styles.memberStat, { color: '#e74c3c' }]}>
                  {member.deaths}
                </Text>
                <Text style={[styles.memberStat, { color: member.bless > 0 ? '#27ae60' : colors.textSecondary }]}>
                  {member.bless > 0 ? `🏮${member.bless}` : '0'}
                </Text>
              </View>
            ))
          ) : (
            <View style={styles.emptyContainer}>
              <MaterialIcons name="inbox" size={48} color={colors.textSecondary} />
              <Text style={[styles.emptyText, { color: colors.textSecondary }]}>暂无成员数据</Text>
            </View>
          )}
        </View>
      );
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {/* 返回按钮 */}
      <TouchableOpacity
        style={[styles.backIconButton, { backgroundColor: colors.cardBackground }]}
        onPress={onBack}
      >
        <MaterialIcons name="arrow-back" size={24} color={colors.text} />
      </TouchableOpacity>

      <ScrollView style={styles.scrollView}>
        {/* 头部信息 */}
        <View style={[styles.header, { backgroundColor: colors.primary }]}>
          <MaterialIcons name="group" size={32} color="#fff" />
          <Text style={styles.groupName}>{groupName}</Text>
          <Text style={styles.subtitle}>分组详情</Text>
        </View>

        {/* 标签页切换 */}
        <View style={[styles.tabContainer, { backgroundColor: colors.cardBackground, borderBottomColor: colors.border }]}>
          <TouchableOpacity
            style={[
              styles.tabButton,
              activeTab === 'kills' && [styles.tabButtonActive, { borderBottomColor: colors.primary }]
            ]}
            onPress={() => setActiveTab('kills')}
          >
            <MaterialIcons 
              name="trending-up" 
              size={20} 
              color={activeTab === 'kills' ? colors.primary : colors.textSecondary} 
            />
            <Text style={[
              styles.tabButtonText,
              { color: activeTab === 'kills' ? colors.primary : colors.textSecondary }
            ]}>
              击杀数据
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.tabButton,
              activeTab === 'members' && [styles.tabButtonActive, { borderBottomColor: colors.primary }]
            ]}
            onPress={() => setActiveTab('members')}
          >
            <MaterialIcons 
              name="bar-chart" 
              size={20} 
              color={activeTab === 'members' ? colors.primary : colors.textSecondary} 
            />
            <Text style={[
              styles.tabButtonText,
              { color: activeTab === 'members' ? colors.primary : colors.textSecondary }
            ]}>
              成员战绩
            </Text>
          </TouchableOpacity>
        </View>

        {/* 标签页内容 */}
        {renderTabContent()}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  backIconButton: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    zIndex: 10,
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  scrollView: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#7f8c8d',
  },
  header: {
    padding: 20,
    paddingTop: 60,
    alignItems: 'center',
  },
  groupName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 12,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  tabContainer: {
    flexDirection: 'row',
    borderBottomWidth: 1,
  },
  tabButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    gap: 6,
  },
  tabButtonActive: {
    borderBottomWidth: 2,
  },
  tabButtonText: {
    fontSize: 14,
    fontWeight: '600',
  },
  detailsSection: {
    padding: 15,
  },
  detailCard: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  detailHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  detailName: {
    fontSize: 14,
    fontWeight: '600',
  },
  detailCount: {
    fontSize: 13,
    fontWeight: 'bold',
  },
  killCount: {
    color: '#27ae60',
  },
  deathCount: {
    color: '#e74c3c',
  },
  detailInfo: {
    flexDirection: 'row',
    marginBottom: 3,
  },
  detailLabel: {
    fontSize: 12,
    width: 50,
  },
  detailValue: {
    fontSize: 12,
    fontWeight: '500',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  noDataText: {
    textAlign: 'center',
    fontSize: 16,
    marginTop: 20,
  },
  membersSection: {
    padding: 12,
  },
  tableHeader: {
    flexDirection: 'row',
    paddingVertical: 8,
    paddingHorizontal: 4,
    borderBottomWidth: 2,
    marginBottom: 4,
  },
  tableHeaderText: {
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  memberRow: {
    flexDirection: 'row',
    paddingVertical: 10,
    paddingHorizontal: 4,
    borderBottomWidth: 1,
    alignItems: 'center',
  },
  memberName: {
    flex: 2,
    fontSize: 13,
    fontWeight: 'bold',
  },
  memberText: {
    flex: 1,
    fontSize: 12,
    textAlign: 'center',
  },
  memberStat: {
    flex: 1,
    fontSize: 13,
    fontWeight: '600',
    textAlign: 'center',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 16,
    marginTop: 12,
  },
});
