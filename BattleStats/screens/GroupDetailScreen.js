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
import { getGroupKillDetails } from '../services/api';

export default function GroupDetailScreen({ groupName, timeRange, onBack }) {
  
  const [loading, setLoading] = useState(true);
  const [killDetails, setKillDetails] = useState([]);
  const [deathDetails, setDeathDetails] = useState([]);
  const [killDirection, setKillDirection] = useState('out');

  useEffect(() => {
    fetchGroupDetails();
  }, []);

  const fetchGroupDetails = async () => {
    try {
      setLoading(true);
      const params = {
        group_name: groupName,
        direction: 'out',
      };
      
      if (timeRange) {
        if (timeRange.startDate && timeRange.endDate) {
          params.start_datetime = formatDateTime(timeRange.startDate);
          params.end_datetime = formatDateTime(timeRange.endDate);
        }
      }
      
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
      
      if (timeRange) {
        if (timeRange.startDate && timeRange.endDate) {
          deathParams.start_datetime = formatDateTime(timeRange.startDate);
          deathParams.end_datetime = formatDateTime(timeRange.endDate);
        }
      }

      const deathResult = await getGroupKillDetails(deathParams);
      
      if (deathResult.success) {
        setDeathDetails(deathResult.data.details || []);
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
    return `${year}-${month}-${day} ${hours}:${minutes}:00`;
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3498db" />
        <Text style={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* 返回按钮 */}
      <TouchableOpacity
        style={styles.backIconButton}
        onPress={onBack}
      >
        <MaterialIcons name="arrow-back" size={24} color="#2c3e50" />
      </TouchableOpacity>

      <ScrollView style={styles.scrollView}>
        {/* 头部信息 */}
        <View style={styles.header}>
          <Text style={styles.groupName}>{groupName}</Text>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>分组详情</Text>
          </View>
        </View>

        {/* 击杀明细 */}
        <View style={styles.detailsSection}>
          <Text style={styles.sectionTitle}>击杀明细</Text>
          {killDetails && killDetails.length > 0 ? (
            killDetails.map((kill, index) => (
              <View key={kill.id || index} style={styles.detailCard}>
                <View style={styles.detailHeader}>
                  <Text style={styles.detailName}>{kill.name}</Text>
                  <Text style={[styles.detailCount, styles.killCount]}>{kill.count}次</Text>
                </View>
                <View style={styles.detailInfo}>
                  <Text style={styles.detailLabel}>职业：</Text>
                  <Text style={styles.detailValue}>{kill.job}</Text>
                </View>
                <View style={styles.detailInfo}>
                  <Text style={styles.detailLabel}>势力：</Text>
                  <Text style={styles.detailValue}>{kill.god}</Text>
                </View>
              </View>
            ))
          ) : (
            <Text style={styles.noDataText}>暂无击杀记录</Text>
          )}
        </View>

        {/* 被杀明细 */}
        <View style={styles.detailsSection}>
          <Text style={styles.sectionTitle}>被杀明细</Text>
          {deathDetails && deathDetails.length > 0 ? (
            deathDetails.map((death, index) => (
              <View key={death.id || index} style={styles.detailCard}>
                <View style={styles.detailHeader}>
                  <Text style={styles.detailName}>{death.name}</Text>
                  <Text style={[styles.detailCount, styles.deathCount]}>{death.count}次</Text>
                </View>
                <View style={styles.detailInfo}>
                  <Text style={styles.detailLabel}>职业：</Text>
                  <Text style={styles.detailValue}>{death.job}</Text>
                </View>
                <View style={styles.detailInfo}>
                  <Text style={styles.detailLabel}>势力：</Text>
                  <Text style={styles.detailValue}>{death.god}</Text>
                </View>
              </View>
            ))
          ) : (
            <Text style={styles.noDataText}>暂无被杀记录</Text>
          )}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f6fa',
  },
  backIconButton: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    zIndex: 10,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
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
    backgroundColor: '#f5f6fa',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#7f8c8d',
  },
  header: {
    backgroundColor: '#2c3e50',
    padding: 20,
    paddingTop: 60,
  },
  groupName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 15,
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  infoLabel: {
    fontSize: 16,
    color: '#bdc3c7',
    width: 60,
  },
  detailsSection: {
    padding: 15,
  },
  detailCard: {
    backgroundColor: '#fff',
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
    color: '#2c3e50',
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
    color: '#7f8c8d',
    width: 50,
  },
  detailValue: {
    fontSize: 12,
    color: '#2c3e50',
    fontWeight: '500',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
  },
  noDataText: {
    textAlign: 'center',
    fontSize: 16,
    color: '#7f8c8d',
    marginTop: 20,
  },
});
