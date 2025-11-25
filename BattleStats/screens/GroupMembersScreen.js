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
import { getGroupDetails } from '../services/api';
import { useTheme } from '../contexts/ThemeContext';

export default function GroupMembersScreen({ groupName, timeRange, onBack }) {
  const { colors } = useTheme();
  const [loading, setLoading] = useState(true);
  const [members, setMembers] = useState([]);

  useEffect(() => {
    fetchGroupMembers();
  }, []);

  const fetchGroupMembers = async () => {
    try {
      setLoading(true);
      const params = {
        player_name: groupName,
      };
      
      if (timeRange) {
        if (timeRange.startDate && timeRange.endDate) {
          params.start_datetime = formatDateTime(timeRange.startDate);
          params.end_datetime = formatDateTime(timeRange.endDate);
        }
      }
      
      const result = await getGroupDetails(params);
      
      if (result.success) {
        setMembers(result.data.members || []);
      } else {
        Alert.alert('错误', result.message || '获取分组成员失败');
      }
    } catch (error) {
      console.error('获取分组成员失败:', error);
      Alert.alert('错误', '获取分组成员失败');
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
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  if (loading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: colors.background }]}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={[styles.loadingText, { color: colors.textSecondary }]}>加载中...</Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {/* 返回按钮 */}
      <TouchableOpacity
        style={[styles.backButton, { backgroundColor: colors.cardBackground }]}
        onPress={onBack}
      >
        <MaterialIcons name="arrow-back" size={24} color={colors.text} />
      </TouchableOpacity>

      <ScrollView style={styles.scrollView}>
        {/* 头部信息 */}
        <View style={[styles.header, { backgroundColor: colors.primary }]}>
          <MaterialIcons name="group" size={32} color="#fff" />
          <Text style={styles.groupName}>{groupName}</Text>
          <Text style={styles.memberCount}>共 {members.length} 个成员</Text>
        </View>

        {/* 成员列表 */}
        <View style={styles.membersSection}>
          {/* 表头 */}
          <View style={[styles.tableHeader, { backgroundColor: colors.cardBackground }]}>
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
                  { backgroundColor: index % 2 === 0 ? colors.cardBackground : colors.background },
                  { borderBottomColor: colors.border }
                ]}
              >
                <Text style={[styles.memberName, { color: colors.text, fontWeight: 'bold' }]} numberOfLines={1}>
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
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  backButton: {
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
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
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
  memberCount: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  membersSection: {
    padding: 12,
  },
  tableHeader: {
    flexDirection: 'row',
    paddingVertical: 8,
    paddingHorizontal: 4,
    borderBottomWidth: 2,
    borderBottomColor: '#e0e0e0',
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
