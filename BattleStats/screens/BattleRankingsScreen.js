import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
  Alert,
  Modal,
  Platform,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { MaterialIcons, FontAwesome5 } from '@expo/vector-icons';
import { getPlayerRankings } from '../services/api';
import PlayerDetailScreen from './PlayerDetailScreen';

// 时间范围选项
const TIME_RANGES = [
  { label: '今天', value: 'today' },
  { label: '昨天', value: 'yesterday' },
  { label: '7天', value: 'week' },
  { label: '30天', value: 'month' },
  { label: '自定义', value: 'custom' },
];

// 势力选项
const FACTIONS = [
  { label: '全部', value: '' },
  { label: '梵天', value: '梵天' },
  { label: '比湿奴', value: '比湿奴' },
  { label: '湿婆', value: '湿婆' },
];

export default function BattleRankingsScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [players, setPlayers] = useState([]);
  const [selectedTime, setSelectedTime] = useState('today');
  const [selectedFaction, setSelectedFaction] = useState('');
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  
  // 自定义时间相关状态
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [datePickerMode, setDatePickerMode] = useState('start'); // 'start' or 'end'
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const [showCustomModal, setShowCustomModal] = useState(false);

  useEffect(() => {
    fetchRankings();
  }, [selectedTime, selectedFaction, startDate, endDate]);

  const fetchRankings = async () => {
    try {
      const params = {
        faction: selectedFaction,
      };
      
      // 如果是自定义时间，使用日期参数
      if (selectedTime === 'custom') {
        params.start_date = formatDate(startDate);
        params.end_date = formatDate(endDate);
      } else {
        params.time_range = selectedTime;
      }
      
      const result = await getPlayerRankings(params);

      if (result.success) {
        // 处理返回的数据，添加 K/D 比率
        const processedData = result.data.rankings.map((player) => ({
          ...player,
          kd_ratio: player.deaths > 0 
            ? (player.kills / player.deaths).toFixed(2) 
            : player.kills.toFixed(2),
        }));
        setPlayers(processedData);
      } else {
        Alert.alert('错误', result.message || '获取排名失败');
        setPlayers([]);
      }
    } catch (error) {
      console.error('获取战绩失败:', error);
      Alert.alert('错误', '网络错误，请稍后重试');
      setPlayers([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };
  
  // 格式化日期为 YYYY-MM-DD
  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };
  
  // 处理时间选择
  const handleTimeSelect = (value) => {
    if (value === 'custom') {
      setShowCustomModal(true);
    } else {
      setSelectedTime(value);
    }
  };
  
  // 处理日期选择
  const onDateChange = (event, selectedDate) => {
    setShowDatePicker(false);
    if (selectedDate) {
      if (datePickerMode === 'start') {
        setStartDate(selectedDate);
      } else {
        setEndDate(selectedDate);
      }
    }
  };
  
  // 确认自定义时间
  const confirmCustomTime = () => {
    if (startDate > endDate) {
      Alert.alert('错误', '开始日期不能晚于结束日期');
      return;
    }
    setSelectedTime('custom');
    setShowCustomModal(false);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchRankings();
    setRefreshing(false);
  };

  // 如果选中了玩家，显示玩家详情
  if (selectedPlayer) {
    return (
      <PlayerDetailScreen
        playerName={selectedPlayer}
        onBack={() => setSelectedPlayer(null)}
      />
    );
  }

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#e74c3c" />
        <Text style={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* 筛选器 */}
      <View style={styles.filterContainer}>
        {/* 时间筛选 */}
        <View style={styles.filterSection}>
          <Text style={styles.filterLabel}>时间范围</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <View style={styles.filterButtons}>
              {TIME_RANGES.map((item) => (
                <TouchableOpacity
                  key={item.value}
                  style={[
                    styles.filterButton,
                    selectedTime === item.value && styles.filterButtonActive,
                  ]}
                  onPress={() => handleTimeSelect(item.value)}
                >
                  <Text
                    style={[
                      styles.filterButtonText,
                      selectedTime === item.value && styles.filterButtonTextActive,
                    ]}
                  >
                    {item.label}
                    {item.value === 'custom' && selectedTime === 'custom' && (
                      <Text style={styles.customDateText}>
                        {'\n'}{formatDate(startDate)} ~ {formatDate(endDate)}
                      </Text>
                    )}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </ScrollView>
        </View>

        {/* 势力筛选 */}
        <View style={styles.filterSection}>
          <Text style={styles.filterLabel}>势力筛选</Text>
          <View style={styles.filterButtons}>
            {FACTIONS.map((item) => (
              <TouchableOpacity
                key={item.value}
                style={[
                  styles.filterButton,
                  selectedFaction === item.value && styles.filterButtonActive,
                ]}
                onPress={() => setSelectedFaction(item.value)}
              >
                <Text
                  style={[
                    styles.filterButtonText,
                    selectedFaction === item.value && styles.filterButtonTextActive,
                  ]}
                >
                  {item.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>

      {/* 排名列表 */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* 表头 */}
        <View style={styles.tableHeader}>
          <Text style={[styles.headerCell, styles.nameCell]}>玩家</Text>
          <Text style={[styles.headerCell, styles.killsCell]}>击杀</Text>
          <Text style={[styles.headerCell, styles.deathsCell]}>死亡</Text>
          <Text style={[styles.headerCell, styles.blessingsCell]}>爆灯</Text>
          <Text style={[styles.headerCell, styles.scoreCell]}>总分</Text>
        </View>

        {/* 数据行 */}
        {players.map((player) => (
          <TouchableOpacity
            key={player.id}
            style={styles.tableRow}
            onPress={() => setSelectedPlayer(player.name)}
          >
            <View style={[styles.cell, styles.nameCell]}>
              <Text style={styles.playerName}>
                {player.name}
              </Text>
              <Text style={styles.jobText}>{player.job}</Text>
            </View>
            <Text style={[styles.cell, styles.killsCell, styles.killsText]}>
              {player.kills}
            </Text>
            <Text style={[styles.cell, styles.deathsCell, styles.deathsText]}>
              {player.deaths}
            </Text>
            <Text style={[styles.cell, styles.blessingsCell, styles.blessingsText]}>
              {player.blessings || 0}
            </Text>
            <Text style={[styles.cell, styles.scoreCell, styles.scoreText]}>
              {player.score}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
      
      {/* 自定义时间选择模态框 */}
      <Modal
        visible={showCustomModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowCustomModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>选择时间范围</Text>
            
            {/* 开始日期 */}
            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => {
                setDatePickerMode('start');
                setShowDatePicker(true);
              }}
            >
              <Text style={styles.dateLabel}>开始日期:</Text>
              <Text style={styles.dateValue}>{formatDate(startDate)}</Text>
            </TouchableOpacity>
            
            {/* 结束日期 */}
            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => {
                setDatePickerMode('end');
                setShowDatePicker(true);
              }}
            >
              <Text style={styles.dateLabel}>结束日期:</Text>
              <Text style={styles.dateValue}>{formatDate(endDate)}</Text>
            </TouchableOpacity>
            
            {/* 按钮组 */}
            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setShowCustomModal(false)}
              >
                <Text style={styles.cancelButtonText}>取消</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.confirmButton]}
                onPress={confirmCustomTime}
              >
                <Text style={styles.confirmButtonText}>确定</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
      
      {/* 日期选择器 */}
      {showDatePicker && (
        <DateTimePicker
          value={datePickerMode === 'start' ? startDate : endDate}
          mode="date"
          display={Platform.OS === 'ios' ? 'spinner' : 'default'}
          onChange={onDateChange}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f6fa',
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
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  filterContainer: {
    backgroundColor: '#fff',
    padding: 12,
    paddingTop: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  filterSection: {
    marginBottom: 10,
  },
  filterLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 6,
  },
  filterButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#ecf0f1',
    marginRight: 8,
    marginBottom: 8,
  },
  filterButtonActive: {
    backgroundColor: '#e74c3c',
  },
  filterButtonText: {
    fontSize: 14,
    color: '#7f8c8d',
    fontWeight: '500',
  },
  filterButtonTextActive: {
    color: '#fff',
  },
  content: {
    flex: 1,
    paddingVertical: 15,
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#e74c3c',
    padding: 12,
    marginBottom: 10,
  },
  headerCell: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
  },
  tableRow: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    padding: 12,
    marginBottom: 1,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  cell: {
    fontSize: 14,
    color: '#2c3e50',
    textAlign: 'center',
  },
  nameCell: {
    flex: 2.5,
    paddingHorizontal: 8,
    justifyContent: 'center',
  },
  playerName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 2,
  },
  jobText: {
    fontSize: 11,
    color: '#7f8c8d',
  },
  killsCell: {
    width: 45,
  },
  deathsCell: {
    width: 45,
  },
  blessingsCell: {
    width: 45,
  },
  scoreCell: {
    width: 55,
  },
  killsText: {
    color: '#27ae60',
    fontWeight: '600',
  },
  deathsText: {
    color: '#e74c3c',
    fontWeight: '600',
  },
  blessingsText: {
    color: '#f39c12',
    fontWeight: '600',
  },
  scoreText: {
    color: '#e74c3c',
    fontWeight: 'bold',
  },
  customDateText: {
    fontSize: 10,
    color: '#fff',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    width: '85%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 20,
    textAlign: 'center',
  },
  dateButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  dateLabel: {
    fontSize: 16,
    color: '#2c3e50',
    fontWeight: '500',
  },
  dateValue: {
    fontSize: 16,
    color: '#e74c3c',
    fontWeight: 'bold',
  },
  modalButtons: {
    flexDirection: 'row',
    marginTop: 20,
    gap: 12,
  },
  modalButton: {
    flex: 1,
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#ecf0f1',
  },
  confirmButton: {
    backgroundColor: '#e74c3c',
  },
  cancelButtonText: {
    color: '#7f8c8d',
    fontSize: 16,
    fontWeight: '600',
  },
  confirmButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
