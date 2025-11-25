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
import { getPlayerRankings, getJobs } from '../services/api';
import PlayerDetailScreen from './PlayerDetailScreen';
import { useTheme } from '../contexts/ThemeContext';

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
  const { colors } = useTheme();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [players, setPlayers] = useState([]);
  const [selectedTime, setSelectedTime] = useState('today');
  const [selectedFaction, setSelectedFaction] = useState('');
  const [selectedJob, setSelectedJob] = useState('');
  const [jobs, setJobs] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [selectedPlayerTimeRange, setSelectedPlayerTimeRange] = useState(null);
  
  // 自定义时间相关状态
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [datePickerMode, setDatePickerMode] = useState('start'); // 'start' or 'end'
  const [tempDate, setTempDate] = useState(new Date()); // 临时存储选择的日期
  const [startDate, setStartDate] = useState(() => {
    const date = new Date();
    date.setHours(0, 0, 0, 0);
    return date;
  });
  const [endDate, setEndDate] = useState(() => {
    const date = new Date();
    date.setHours(23, 59, 0, 0);
    return date;
  });
  const [showCustomModal, setShowCustomModal] = useState(false);

  useEffect(() => {
    fetchJobs();
    fetchRankings();
  }, [selectedTime, selectedFaction, selectedJob, startDate, endDate]);

  const fetchJobs = async () => {
    try {
      const result = await getJobs();
      if (result.success) {
        setJobs(result.data);
      }
    } catch (error) {
      console.error('获取职业列表失败:', error);
    }
  };

  const fetchRankings = async () => {
    try {
      const params = {
        faction: selectedFaction,
        job: selectedJob,
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
  
  // 格式化日期时间为 YYYY-MM-DD HH:MM
  const formatDateTime = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
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
    if (Platform.OS === 'android') {
      setShowDatePicker(false);
      if (event.type === 'set' && selectedDate) {
        // Android: 选择日期后,打开时间选择器
        setTempDate(selectedDate);
        setShowTimePicker(true);
      }
    } else {
      // iOS: 直接更新日期时间
      if (selectedDate) {
        if (datePickerMode === 'start') {
          setStartDate(selectedDate);
        } else {
          setEndDate(selectedDate);
        }
      }
    }
  };
  
  // 处理时间选择
  const onTimeChange = (event, selectedTime) => {
    setShowTimePicker(false);
    
    if (event.type === 'set' && selectedTime) {
      // 合并日期和时间
      const finalDate = new Date(tempDate);
      finalDate.setHours(selectedTime.getHours());
      finalDate.setMinutes(selectedTime.getMinutes());
      finalDate.setSeconds(0);
      finalDate.setMilliseconds(0);
      
      if (datePickerMode === 'start') {
        setStartDate(finalDate);
      } else {
        setEndDate(finalDate);
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
        timeRange={selectedPlayerTimeRange}
        onBack={() => setSelectedPlayer(null)}
      />
    );
  }

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
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
                    selectedTime === item.value && { backgroundColor: colors.primary },
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
                        {' \n'}{formatDateTime(startDate)}{' \n'}至 {formatDateTime(endDate)}
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
                  selectedFaction === item.value && { backgroundColor: colors.primary },
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

        {/* 职业筛选 */}
        <View style={styles.filterSection}>
          <Text style={styles.filterLabel}>职业筛选</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <View style={styles.filterButtons}>
              <TouchableOpacity
                style={[
                  styles.filterButton,
                  selectedJob === '' && { backgroundColor: colors.primary },
                ]}
                onPress={() => setSelectedJob('')}
              >
                <Text
                  style={[
                    styles.filterButtonText,
                    selectedJob === '' && styles.filterButtonTextActive,
                  ]}
                >
                  全部
                </Text>
              </TouchableOpacity>
              {jobs.map((job) => (
                <TouchableOpacity
                  key={job}
                  style={[
                    styles.filterButton,
                    selectedJob === job && { backgroundColor: colors.primary },
                  ]}
                  onPress={() => setSelectedJob(job)}
                >
                  <Text
                    style={[
                      styles.filterButtonText,
                      selectedJob === job && styles.filterButtonTextActive,
                    ]}
                  >
                    {job}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </ScrollView>
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
        <View style={[styles.tableHeader, { backgroundColor: colors.primary }]}>
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
            onPress={() => {
              setSelectedPlayer(player.name);
              setSelectedPlayerTimeRange(selectedTime === 'custom' ? { startDate, endDate } : { timeRange: selectedTime });
            }}
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
            
            {/* 开始日期时间 */}
            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => {
                setDatePickerMode('start');
                setTempDate(startDate);
                setShowDatePicker(true);
              }}
            >
              <Text style={styles.dateLabel}>开始时间:</Text>
              <Text style={styles.dateValue}>{formatDateTime(startDate)}</Text>
            </TouchableOpacity>
            
            {/* 结束日期时间 */}
            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => {
                setDatePickerMode('end');
                setTempDate(endDate);
                setShowDatePicker(true);
              }}
            >
              <Text style={styles.dateLabel}>结束时间:</Text>
              <Text style={styles.dateValue}>{formatDateTime(endDate)}</Text>
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
                style={[styles.modalButton, { backgroundColor: colors.primary }]}
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
          value={tempDate}
          mode={Platform.OS === 'ios' ? 'datetime' : 'date'}
          display={Platform.OS === 'ios' ? 'spinner' : 'default'}
          onChange={onDateChange}
        />
      )}
      
      {/* 时间选择器 (仅 Android) */}
      {showTimePicker && Platform.OS === 'android' && (
        <DateTimePicker
          value={tempDate}
          mode="time"
          is24Hour={true}
          display="default"
          onChange={onTimeChange}
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
    padding: 15,
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#e74c3c',
    padding: 12,
    borderRadius: 8,
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
    borderRadius: 8,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
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
