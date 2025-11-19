import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  Alert,
  Modal,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'https://bigmang.xyz';
const TOKEN_KEY = '@battle_stats_token';

// 主神选项
const GOD_OPTIONS = ['梵天', '比湿奴', '湿婆'];

// 主神颜色
const GOD_COLORS = {
  '梵天': '#f39c12',
  '比湿奴': '#e74c3c',
  '湿婆': '#3498db',
};

// 战盟选项
const UNION_OPTIONS = ['梵天战盟', '逍遥战盟', '蓝神战盟'];

// 职业选项
const JOB_OPTIONS = ['狂', '奶', '金刚', '护法', '法师', '弓', '刺客'];

// 等级选项
const LEVEL_OPTIONS = [
  { label: '马哈拉', value: '1' },
  { label: '阿尔瓦', value: '2' },
  { label: '婆罗门', value: '3' },
  { label: '刹帝利', value: '4' },
  { label: '狗狗级', value: '5' },
];

export default function PersonManagementScreen() {
  const [persons, setPersons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  // 筛选条件
  const [searchText, setSearchText] = useState('');
  const [selectedGod, setSelectedGod] = useState('');
  const [selectedJob, setSelectedJob] = useState('');
  const [availableJobs, setAvailableJobs] = useState([]);
  
  // 模态框状态
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [editingPerson, setEditingPerson] = useState(null);
  
  // 表单数据
  const [formData, setFormData] = useState({
    name: '',
    god: '',
    union_name: '',
    job: '',
    level: '',
  });

  useEffect(() => {
    fetchPersons();
  }, [page, searchText, selectedGod, selectedJob]);

  // 获取人员列表
  const fetchPersons = async () => {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '20',
      });
      
      if (searchText) params.append('search', searchText);
      if (selectedGod) params.append('god', selectedGod);
      if (selectedJob) params.append('job', selectedJob);

      const response = await fetch(`${API_BASE_URL}/api/person/list?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const result = await response.json();

      if (result.status === 'success') {
        setPersons(result.data.persons);
        setTotalPages(result.data.pages);
        setAvailableJobs(result.data.available_jobs || []);
      } else {
        Alert.alert('错误', result.message);
      }
    } catch (error) {
      console.error('获取人员列表失败:', error);
      Alert.alert('错误', '获取人员列表失败');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // 添加人员
  const handleAdd = async () => {
    if (!formData.name || !formData.god) {
      Alert.alert('提示', '请填写游戏ID和主神');
      return;
    }

    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      const response = await fetch(`${API_BASE_URL}/api/person/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (result.status === 'success') {
        Alert.alert('成功', '添加成功');
        setShowAddModal(false);
        resetForm();
        fetchPersons();
      } else {
        Alert.alert('错误', result.message);
      }
    } catch (error) {
      console.error('添加失败:', error);
      Alert.alert('错误', '添加失败');
    }
  };

  // 编辑人员
  const handleEdit = async () => {
    if (!formData.name || !formData.god) {
      Alert.alert('提示', '请填写游戏ID和主神');
      return;
    }

    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      const response = await fetch(`${API_BASE_URL}/api/person/edit/${editingPerson.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (result.status === 'success') {
        Alert.alert('成功', '更新成功');
        setShowEditModal(false);
        resetForm();
        fetchPersons();
      } else {
        Alert.alert('错误', result.message);
      }
    } catch (error) {
      console.error('更新失败:', error);
      Alert.alert('错误', '更新失败');
    }
  };

  // 删除人员
  const handleDelete = (person) => {
    Alert.alert(
      '确认删除',
      `确定要删除 ${person.name} 吗？`,
      [
        { text: '取消', style: 'cancel' },
        {
          text: '删除',
          style: 'destructive',
          onPress: async () => {
            try {
              const token = await AsyncStorage.getItem(TOKEN_KEY);
              const response = await fetch(`${API_BASE_URL}/api/person/delete/${person.id}`, {
                method: 'DELETE',
                headers: {
                  'Authorization': `Bearer ${token}`,
                },
              });

              const result = await response.json();

              if (result.status === 'success') {
                Alert.alert('成功', '删除成功');
                fetchPersons();
              } else {
                Alert.alert('错误', result.message);
              }
            } catch (error) {
              console.error('删除失败:', error);
              Alert.alert('错误', '删除失败');
            }
          },
        },
      ]
    );
  };

  // 打开编辑模态框
  const openEditModal = (person) => {
    setEditingPerson(person);
    setFormData({
      name: person.name,
      god: person.god,
      union_name: person.union_name || '',
      job: person.job || '',
      level: person.level || '',
    });
    setShowEditModal(true);
  };

  // 重置表单
  const resetForm = () => {
    setFormData({
      name: '',
      god: '',
      union_name: '',
      job: '',
      level: '',
    });
    setEditingPerson(null);
  };

  // 下拉刷新
  const onRefresh = () => {
    setRefreshing(true);
    setPage(1);
    fetchPersons();
  };

  // 渲染人员卡片
  const renderPersonCard = ({ item }) => (
    <View style={styles.personCard}>
      <View style={styles.personHeader}>
        <View style={styles.personInfo}>
          <Text style={styles.personName}>{item.name}</Text>
          <View style={[styles.godBadge, { backgroundColor: GOD_COLORS[item.god] }]}>
            <Text style={styles.godText}>{item.god}</Text>
          </View>
        </View>
        <View style={styles.personActions}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => openEditModal(item)}
          >
            <MaterialIcons name="edit" size={20} color="#3498db" />
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => handleDelete(item)}
          >
            <MaterialIcons name="delete" size={20} color="#e74c3c" />
          </TouchableOpacity>
        </View>
      </View>
      
      <View style={styles.personDetails}>
        {item.union_name && (
          <View style={styles.detailRow}>
            <MaterialIcons name="group" size={16} color="#7f8c8d" />
            <Text style={styles.detailText}>{item.union_name}</Text>
          </View>
        )}
        {item.job && (
          <View style={styles.detailRow}>
            <MaterialIcons name="work" size={16} color="#7f8c8d" />
            <Text style={styles.detailText}>{item.job}</Text>
          </View>
        )}
        {item.level && (
          <View style={styles.detailRow}>
            <MaterialIcons name="star" size={16} color="#7f8c8d" />
            <Text style={styles.detailText}>{item.level}</Text>
          </View>
        )}
      </View>
    </View>
  );

  // 渲染表单模态框
  const renderFormModal = (visible, onClose, onSubmit, title) => (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>{title}</Text>
            <TouchableOpacity onPress={onClose}>
              <MaterialIcons name="close" size={24} color="#2c3e50" />
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.formContainer}>
            {/* 游戏ID */}
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>游戏ID *</Text>
              <TextInput
                style={styles.formInput}
                value={formData.name}
                onChangeText={(text) => setFormData({ ...formData, name: text })}
                placeholder="请输入游戏ID"
              />
            </View>

            {/* 主神 */}
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>主神 *</Text>
              <View style={styles.godSelector}>
                {GOD_OPTIONS.map((god) => (
                  <TouchableOpacity
                    key={god}
                    style={[
                      styles.godOption,
                      formData.god === god && { backgroundColor: GOD_COLORS[god] },
                    ]}
                    onPress={() => setFormData({ ...formData, god })}
                  >
                    <Text
                      style={[
                        styles.godOptionText,
                        formData.god === god && styles.godOptionTextActive,
                      ]}
                    >
                      {god}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* 联盟 */}
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>联盟 *</Text>
              <View style={styles.optionSelector}>
                {UNION_OPTIONS.map((union) => (
                  <TouchableOpacity
                    key={union}
                    style={[
                      styles.option,
                      formData.union_name === union && styles.optionActive,
                    ]}
                    onPress={() => setFormData({ ...formData, union_name: union })}
                  >
                    <Text
                      style={[
                        styles.optionText,
                        formData.union_name === union && styles.optionTextActive,
                      ]}
                    >
                      {union}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* 职业 */}
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>职业 *</Text>
              <View style={styles.optionSelector}>
                {JOB_OPTIONS.map((job) => (
                  <TouchableOpacity
                    key={job}
                    style={[
                      styles.option,
                      formData.job === job && styles.optionActive,
                    ]}
                    onPress={() => setFormData({ ...formData, job })}
                  >
                    <Text
                      style={[
                        styles.optionText,
                        formData.job === job && styles.optionTextActive,
                      ]}
                    >
                      {job}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* 等级 */}
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>主神级别 *</Text>
              <View style={styles.optionSelector}>
                {LEVEL_OPTIONS.map((level) => (
                  <TouchableOpacity
                    key={level.value}
                    style={[
                      styles.option,
                      formData.level === level.value && styles.optionActive,
                    ]}
                    onPress={() => setFormData({ ...formData, level: level.value })}
                  >
                    <Text
                      style={[
                        styles.optionText,
                        formData.level === level.value && styles.optionTextActive,
                      ]}
                    >
                      {level.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </ScrollView>

          <View style={styles.modalButtons}>
            <TouchableOpacity
              style={[styles.modalButton, styles.cancelButton]}
              onPress={onClose}
            >
              <Text style={styles.cancelButtonText}>取消</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.modalButton, styles.confirmButton]}
              onPress={onSubmit}
            >
              <Text style={styles.confirmButtonText}>确定</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );

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
      {/* 搜索和筛选栏 */}
      <View style={styles.searchBar}>
        <View style={styles.searchInputContainer}>
          <MaterialIcons name="search" size={20} color="#7f8c8d" />
          <TextInput
            style={styles.searchInput}
            value={searchText}
            onChangeText={setSearchText}
            placeholder="搜索游戏ID、联盟、职业"
            placeholderTextColor="#95a5a6"
          />
        </View>
        <TouchableOpacity
          style={styles.filterButton}
          onPress={() => setShowFilterModal(true)}
        >
          <MaterialIcons name="filter-list" size={24} color="#fff" />
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => {
            resetForm();
            setShowAddModal(true);
          }}
        >
          <MaterialIcons name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      {/* 人员列表 */}
      <FlatList
        data={persons}
        renderItem={renderPersonCard}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <MaterialIcons name="people-outline" size={64} color="#bdc3c7" />
            <Text style={styles.emptyText}>暂无人员数据</Text>
          </View>
        }
      />

      {/* 添加模态框 */}
      {renderFormModal(
        showAddModal,
        () => {
          setShowAddModal(false);
          resetForm();
        },
        handleAdd,
        '添加人员'
      )}

      {/* 编辑模态框 */}
      {renderFormModal(
        showEditModal,
        () => {
          setShowEditModal(false);
          resetForm();
        },
        handleEdit,
        '编辑人员'
      )}

      {/* 筛选模态框 */}
      <Modal
        visible={showFilterModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowFilterModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>筛选条件</Text>
              <TouchableOpacity onPress={() => setShowFilterModal(false)}>
                <MaterialIcons name="close" size={24} color="#2c3e50" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.filterContainer}>
              {/* 主神筛选 */}
              <View style={styles.filterSection}>
                <Text style={styles.filterLabel}>主神</Text>
                <View style={styles.filterOptions}>
                  <TouchableOpacity
                    style={[
                      styles.filterOption,
                      !selectedGod && styles.filterOptionActive,
                    ]}
                    onPress={() => setSelectedGod('')}
                  >
                    <Text
                      style={[
                        styles.filterOptionText,
                        !selectedGod && styles.filterOptionTextActive,
                      ]}
                    >
                      全部
                    </Text>
                  </TouchableOpacity>
                  {GOD_OPTIONS.map((god) => (
                    <TouchableOpacity
                      key={god}
                      style={[
                        styles.filterOption,
                        selectedGod === god && styles.filterOptionActive,
                      ]}
                      onPress={() => setSelectedGod(god)}
                    >
                      <Text
                        style={[
                          styles.filterOptionText,
                          selectedGod === god && styles.filterOptionTextActive,
                        ]}
                      >
                        {god}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>

              {/* 职业筛选 */}
              {availableJobs.length > 0 && (
                <View style={styles.filterSection}>
                  <Text style={styles.filterLabel}>职业</Text>
                  <View style={styles.filterOptions}>
                    <TouchableOpacity
                      style={[
                        styles.filterOption,
                        !selectedJob && styles.filterOptionActive,
                      ]}
                      onPress={() => setSelectedJob('')}
                    >
                      <Text
                        style={[
                          styles.filterOptionText,
                          !selectedJob && styles.filterOptionTextActive,
                        ]}
                      >
                        全部
                      </Text>
                    </TouchableOpacity>
                    {availableJobs.map((job) => (
                      <TouchableOpacity
                        key={job}
                        style={[
                          styles.filterOption,
                          selectedJob === job && styles.filterOptionActive,
                        ]}
                        onPress={() => setSelectedJob(job)}
                      >
                        <Text
                          style={[
                            styles.filterOptionText,
                            selectedJob === job && styles.filterOptionTextActive,
                          ]}
                        >
                          {job}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
              )}
            </ScrollView>

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => {
                  setSelectedGod('');
                  setSelectedJob('');
                }}
              >
                <Text style={styles.cancelButtonText}>重置</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.confirmButton]}
                onPress={() => {
                  setShowFilterModal(false);
                  setPage(1);
                  fetchPersons();
                }}
              >
                <Text style={styles.confirmButtonText}>确定</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
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
  searchBar: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
    alignItems: 'center',
    gap: 8,
  },
  searchInputContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    paddingHorizontal: 12,
    height: 40,
  },
  searchInput: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
    color: '#2c3e50',
  },
  filterButton: {
    backgroundColor: '#95a5a6',
    width: 40,
    height: 40,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  addButton: {
    backgroundColor: '#e74c3c',
    width: 40,
    height: 40,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContainer: {
    padding: 12,
  },
  personCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  personHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  personInfo: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  personName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginRight: 10,
  },
  godBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  godText: {
    fontSize: 12,
    color: '#fff',
    fontWeight: '600',
  },
  personActions: {
    flexDirection: 'row',
    gap: 8,
  },
  actionButton: {
    padding: 8,
  },
  personDetails: {
    gap: 6,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  detailText: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    marginTop: 12,
    fontSize: 16,
    color: '#95a5a6',
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
    width: '90%',
    maxHeight: '80%',
    overflow: 'hidden',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  formContainer: {
    padding: 16,
  },
  formGroup: {
    marginBottom: 16,
  },
  formLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 8,
  },
  formInput: {
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#2c3e50',
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  godSelector: {
    flexDirection: 'row',
    gap: 8,
  },
  godOption: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 8,
    backgroundColor: '#f8f9fa',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  godOptionText: {
    fontSize: 14,
    color: '#7f8c8d',
    fontWeight: '600',
  },
  godOptionTextActive: {
    color: '#fff',
  },
  optionSelector: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  option: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    backgroundColor: '#f8f9fa',
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  optionActive: {
    backgroundColor: '#e74c3c',
    borderColor: '#e74c3c',
  },
  optionText: {
    fontSize: 14,
    color: '#7f8c8d',
    fontWeight: '500',
  },
  optionTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  modalButtons: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
    borderTopWidth: 1,
    borderTopColor: '#ecf0f1',
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
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
  filterContainer: {
    padding: 16,
  },
  filterSection: {
    marginBottom: 20,
  },
  filterLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 10,
  },
  filterOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  filterOption: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f8f9fa',
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  filterOptionActive: {
    backgroundColor: '#e74c3c',
    borderColor: '#e74c3c',
  },
  filterOptionText: {
    fontSize: 14,
    color: '#7f8c8d',
    fontWeight: '500',
  },
  filterOptionTextActive: {
    color: '#fff',
  },
});
