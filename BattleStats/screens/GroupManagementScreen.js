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

export default function GroupManagementScreen() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchText, setSearchText] = useState('');
  
  // 模态框状态
  const [modalVisible, setModalVisible] = useState(false);
  const [editingGroup, setEditingGroup] = useState(null);
  const [formData, setFormData] = useState({
    group_name: '',
    description: '',
    player_ids: [],
  });
  
  // 玩家选择
  const [availablePlayers, setAvailablePlayers] = useState([]);
  const [selectedPlayers, setSelectedPlayers] = useState([]);
  const [playerModalVisible, setPlayerModalVisible] = useState(false);

  useEffect(() => {
    fetchGroups();
  }, [searchText]);

  // 获取分组列表
  const fetchGroups = async () => {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      const params = new URLSearchParams({
        page: '1',
        per_page: '100',
      });
      
      if (searchText) params.append('search', searchText);

      const response = await fetch(`${API_BASE_URL}/api/player_group/list?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const result = await response.json();

      if (result.status === 'success') {
        setGroups(result.data.groups);
      } else {
        Alert.alert('错误', result.message || '获取分组列表失败');
      }
    } catch (error) {
      console.error('获取分组列表失败:', error);
      Alert.alert('错误', '获取分组列表失败');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // 获取可用玩家列表
  const fetchAvailablePlayers = async () => {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      const response = await fetch(`${API_BASE_URL}/api/player_group/available-players`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const result = await response.json();

      if (result.status === 'success') {
        setAvailablePlayers(result.data);
      }
    } catch (error) {
      console.error('获取可用玩家失败:', error);
    }
  };

  // 添加分组
  const handleAdd = async () => {
    if (!formData.group_name) {
      Alert.alert('提示', '请填写分组名称');
      return;
    }

    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      const response = await fetch(`${API_BASE_URL}/api/player_group/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...formData,
          player_ids: selectedPlayers.map(p => p.id),
        }),
      });

      const result = await response.json();

      if (result.status === 'success') {
        Alert.alert('成功', '添加成功');
        setModalVisible(false);
        resetForm();
        fetchGroups();
      } else {
        Alert.alert('错误', result.message || '添加失败');
      }
    } catch (error) {
      console.error('添加分组失败:', error);
      Alert.alert('错误', '添加失败');
    }
  };

  // 编辑分组
  const handleEdit = async () => {
    if (!formData.group_name) {
      Alert.alert('提示', '请填写分组名称');
      return;
    }

    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      const response = await fetch(`${API_BASE_URL}/api/player_group/edit/${editingGroup.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...formData,
          player_ids: selectedPlayers.map(p => p.id),
        }),
      });

      const result = await response.json();

      if (result.status === 'success') {
        Alert.alert('成功', '更新成功');
        setModalVisible(false);
        resetForm();
        fetchGroups();
      } else {
        Alert.alert('错误', result.message || '更新失败');
      }
    } catch (error) {
      console.error('更新分组失败:', error);
      Alert.alert('错误', '更新失败');
    }
  };

  // 删除分组
  const handleDelete = (group) => {
    Alert.alert(
      '确认删除',
      `确定要删除分组 ${group.group_name} 吗？`,
      [
        { text: '取消', style: 'cancel' },
        {
          text: '删除',
          style: 'destructive',
          onPress: async () => {
            try {
              const token = await AsyncStorage.getItem(TOKEN_KEY);
              const response = await fetch(`${API_BASE_URL}/api/player_group/delete/${group.id}`, {
                method: 'DELETE',
                headers: {
                  'Authorization': `Bearer ${token}`,
                },
              });

              const result = await response.json();

              if (result.status === 'success') {
                Alert.alert('成功', '删除成功');
                fetchGroups();
              } else {
                Alert.alert('错误', result.message || '删除失败');
              }
            } catch (error) {
              console.error('删除分组失败:', error);
              Alert.alert('错误', '删除失败');
            }
          },
        },
      ]
    );
  };

  // 打开添加模态框
  const openAddModal = async () => {
    await fetchAvailablePlayers();
    setEditingGroup(null);
    setFormData({ group_name: '', description: '', player_ids: [] });
    setSelectedPlayers([]);
    setModalVisible(true);
  };

  // 打开编辑模态框
  const openEditModal = async (group) => {
    await fetchAvailablePlayers();
    setEditingGroup(group);
    setFormData({
      group_name: group.group_name,
      description: group.description || '',
      player_ids: group.players.map(p => p.id),
    });
    setSelectedPlayers(group.players);
    setModalVisible(true);
  };

  // 重置表单
  const resetForm = () => {
    setEditingGroup(null);
    setFormData({ group_name: '', description: '', player_ids: [] });
    setSelectedPlayers([]);
  };

  // 切换玩家选择
  const togglePlayerSelection = (player) => {
    const isSelected = selectedPlayers.some(p => p.id === player.id);
    if (isSelected) {
      setSelectedPlayers(selectedPlayers.filter(p => p.id !== player.id));
    } else {
      setSelectedPlayers([...selectedPlayers, player]);
    }
  };

  // 下拉刷新
  const onRefresh = () => {
    setRefreshing(true);
    fetchGroups();
  };

  // 渲染分组卡片
  const renderGroupCard = ({ item }) => (
    <View style={styles.groupCard}>
      <View style={styles.groupHeader}>
        <View style={styles.groupInfo}>
          <Text style={styles.groupName}>{item.group_name}</Text>
          {item.description ? (
            <Text style={styles.groupDescription}>{item.description}</Text>
          ) : null}
        </View>
        <View style={styles.groupActions}>
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

      {/* 玩家列表 */}
      <View style={styles.playerList}>
        <Text style={styles.playerListTitle}>
          成员 ({item.player_count})
        </Text>
        {item.players.length > 0 ? (
          <View style={styles.playerTags}>
            {item.players.map((player) => (
              <View key={player.id} style={styles.playerTag}>
                <Text style={styles.playerTagText}>{player.name}</Text>
                {player.job ? (
                  <Text style={styles.playerJobText}> · {player.job}</Text>
                ) : null}
              </View>
            ))}
          </View>
        ) : (
          <Text style={styles.emptyPlayerText}>暂无成员</Text>
        )}
      </View>
    </View>
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
      {/* 搜索栏 */}
      <View style={styles.searchBar}>
        <MaterialIcons name="search" size={20} color="#7f8c8d" />
        <TextInput
          style={styles.searchInput}
          placeholder="搜索分组名称或描述"
          value={searchText}
          onChangeText={setSearchText}
        />
        <TouchableOpacity style={styles.addButton} onPress={openAddModal}>
          <MaterialIcons name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      {/* 分组列表 */}
      <FlatList
        data={groups}
        renderItem={renderGroupCard}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <MaterialIcons name="group" size={64} color="#bdc3c7" />
            <Text style={styles.emptyText}>暂无分组</Text>
          </View>
        }
      />

      {/* 添加/编辑模态框 */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>
                {editingGroup ? '编辑分组' : '添加分组'}
              </Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <MaterialIcons name="close" size={24} color="#2c3e50" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              {/* 分组名称 */}
              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>分组名称 *</Text>
                <TextInput
                  style={styles.formInput}
                  value={formData.group_name}
                  onChangeText={(text) => setFormData({ ...formData, group_name: text })}
                  placeholder="请输入分组名称"
                />
              </View>

              {/* 描述 */}
              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>描述</Text>
                <TextInput
                  style={[styles.formInput, styles.textArea]}
                  value={formData.description}
                  onChangeText={(text) => setFormData({ ...formData, description: text })}
                  placeholder="请输入描述"
                  multiline
                  numberOfLines={3}
                />
              </View>

              {/* 选择玩家 */}
              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>选择成员</Text>
                <TouchableOpacity
                  style={styles.selectButton}
                  onPress={() => setPlayerModalVisible(true)}
                >
                  <Text style={styles.selectButtonText}>
                    {selectedPlayers.length > 0
                      ? `已选择 ${selectedPlayers.length} 个成员`
                      : '点击选择成员'}
                  </Text>
                  <MaterialIcons name="chevron-right" size={20} color="#7f8c8d" />
                </TouchableOpacity>

                {/* 已选择的玩家 */}
                {selectedPlayers.length > 0 && (
                  <View style={styles.selectedPlayers}>
                    {selectedPlayers.map((player) => (
                      <View key={player.id} style={styles.selectedPlayerTag}>
                        <Text style={styles.selectedPlayerText}>{player.name}</Text>
                        <TouchableOpacity onPress={() => togglePlayerSelection(player)}>
                          <MaterialIcons name="close" size={16} color="#fff" />
                        </TouchableOpacity>
                      </View>
                    ))}
                  </View>
                )}
              </View>
            </ScrollView>

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.cancelButtonText}>取消</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.confirmButton]}
                onPress={editingGroup ? handleEdit : handleAdd}
              >
                <Text style={styles.confirmButtonText}>确定</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* 玩家选择模态框 */}
      <Modal
        visible={playerModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setPlayerModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>选择成员</Text>
              <TouchableOpacity onPress={() => setPlayerModalVisible(false)}>
                <MaterialIcons name="close" size={24} color="#2c3e50" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              {/* 当前分组的玩家 */}
              {editingGroup && editingGroup.players.length > 0 && (
                <View style={styles.playerSection}>
                  <Text style={styles.sectionTitle}>当前成员</Text>
                  {editingGroup.players.map((player) => {
                    const isSelected = selectedPlayers.some(p => p.id === player.id);
                    return (
                      <TouchableOpacity
                        key={player.id}
                        style={[styles.playerItem, isSelected && styles.playerItemSelected]}
                        onPress={() => togglePlayerSelection(player)}
                      >
                        <View style={styles.playerItemInfo}>
                          <Text style={styles.playerItemName}>{player.name}</Text>
                          <Text style={styles.playerItemDetail}>
                            {player.god} · {player.job}
                          </Text>
                        </View>
                        {isSelected && (
                          <MaterialIcons name="check-circle" size={24} color="#e74c3c" />
                        )}
                      </TouchableOpacity>
                    );
                  })}
                </View>
              )}

              {/* 可用玩家 */}
              {availablePlayers.length > 0 && (
                <View style={styles.playerSection}>
                  <Text style={styles.sectionTitle}>可用玩家</Text>
                  {availablePlayers.map((player) => {
                    const isSelected = selectedPlayers.some(p => p.id === player.id);
                    return (
                      <TouchableOpacity
                        key={player.id}
                        style={[styles.playerItem, isSelected && styles.playerItemSelected]}
                        onPress={() => togglePlayerSelection(player)}
                      >
                        <View style={styles.playerItemInfo}>
                          <Text style={styles.playerItemName}>{player.name}</Text>
                          <Text style={styles.playerItemDetail}>
                            {player.god} · {player.job}
                          </Text>
                        </View>
                        {isSelected && (
                          <MaterialIcons name="check-circle" size={24} color="#e74c3c" />
                        )}
                      </TouchableOpacity>
                    );
                  })}
                </View>
              )}

              {availablePlayers.length === 0 && (!editingGroup || editingGroup.players.length === 0) && (
                <View style={styles.emptyContainer}>
                  <Text style={styles.emptyText}>暂无可用玩家</Text>
                </View>
              )}
            </ScrollView>

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.confirmButton]}
                onPress={() => setPlayerModalVisible(false)}
              >
                <Text style={styles.confirmButtonText}>完成</Text>
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
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 12,
    gap: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  searchInput: {
    flex: 1,
    fontSize: 14,
    color: '#2c3e50',
  },
  addButton: {
    backgroundColor: '#e74c3c',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContent: {
    padding: 15,
  },
  groupCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  groupHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  groupInfo: {
    flex: 1,
  },
  groupName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 4,
  },
  groupDescription: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  groupActions: {
    flexDirection: 'row',
    gap: 8,
  },
  actionButton: {
    padding: 8,
  },
  playerList: {
    borderTopWidth: 1,
    borderTopColor: '#ecf0f1',
    paddingTop: 12,
  },
  playerListTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 8,
  },
  playerTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  playerTag: {
    flexDirection: 'row',
    backgroundColor: '#ecf0f1',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  playerTagText: {
    fontSize: 13,
    color: '#2c3e50',
    fontWeight: '500',
  },
  playerJobText: {
    fontSize: 13,
    color: '#7f8c8d',
  },
  emptyPlayerText: {
    fontSize: 14,
    color: '#95a5a6',
    fontStyle: 'italic',
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
    fontWeight: '600',
    color: '#2c3e50',
  },
  modalBody: {
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
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  selectButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 12,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  selectButtonText: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  selectedPlayers: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 8,
  },
  selectedPlayerTag: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#e74c3c',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    gap: 6,
  },
  selectedPlayerText: {
    fontSize: 13,
    color: '#fff',
    fontWeight: '500',
  },
  playerSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 12,
  },
  playerItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  playerItemSelected: {
    backgroundColor: '#fee',
    borderWidth: 1,
    borderColor: '#e74c3c',
  },
  playerItemInfo: {
    flex: 1,
  },
  playerItemName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 4,
  },
  playerItemDetail: {
    fontSize: 13,
    color: '#7f8c8d',
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
    fontSize: 16,
    fontWeight: '600',
    color: '#7f8c8d',
  },
  confirmButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
});
