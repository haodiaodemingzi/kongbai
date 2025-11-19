import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import * as DocumentPicker from 'expo-document-picker';
import { uploadBattleLog } from '../services/api';

export default function UploadScreen() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  // 选择文件
  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'text/plain', // 只允许选择文本文件
        copyToCacheDirectory: true,
      });

      if (result.type === 'success' || !result.canceled) {
        const file = result.assets ? result.assets[0] : result;
        
        // 检查文件扩展名
        if (!file.name.endsWith('.txt')) {
          Alert.alert('错误', '只支持 .txt 格式的文件');
          return;
        }

        setSelectedFile(file);
        Alert.alert('成功', `已选择文件: ${file.name}`);
      }
    } catch (error) {
      console.error('选择文件失败:', error);
      Alert.alert('错误', '选择文件失败');
    }
  };

  // 上传文件
  const handleUpload = async () => {
    if (!selectedFile) {
      Alert.alert('提示', '请先选择文件');
      return;
    }

    setUploading(true);

    try {
      const result = await uploadBattleLog(selectedFile);

      if (result.success) {
        Alert.alert(
          '上传成功',
          result.message || '战斗日志已成功上传并解析',
          [
            {
              text: '确定',
              onPress: () => {
                setSelectedFile(null);
              },
            },
          ]
        );
      } else {
        Alert.alert('上传失败', result.message || '上传失败，请重试');
      }
    } catch (error) {
      console.error('上传失败:', error);
      Alert.alert('错误', error.message || '上传失败，请检查网络连接');
    } finally {
      setUploading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* 说明卡片 */}
        <View style={styles.infoCard}>
          <View style={styles.infoHeader}>
            <MaterialIcons name="info" size={24} color="#3498db" />
            <Text style={styles.infoTitle}>日志格式说明</Text>
          </View>
          <Text style={styles.infoText}>系统支持解析以下格式的日志：</Text>
          <View style={styles.formatList}>
            <Text style={styles.formatItem}>
              • 击杀记录：[战况]玩家A 击杀 玩家B !坐标:X，Y  (YYYYMMDD,HH:MM:SS)
            </Text>
            <Text style={styles.formatItem}>
              • 祝福记录：[公告]  玩家A 得到了 XX祝福 的祝福! (YYYYMMDD,HH:MM:SS)
            </Text>
          </View>
          <Text style={styles.infoNote}>
            请上传TXT格式的战斗日志文件，文件编码应为GBK。
          </Text>
        </View>

        {/* 文件选择区域 */}
        <View style={styles.uploadCard}>
          <TouchableOpacity
            style={styles.selectButton}
            onPress={pickDocument}
            disabled={uploading}
          >
            <MaterialIcons name="folder-open" size={48} color="#e74c3c" />
            <Text style={styles.selectButtonText}>选择战斗日志文件</Text>
            <Text style={styles.selectButtonHint}>点击选择 .txt 文件</Text>
          </TouchableOpacity>

          {/* 已选择的文件 */}
          {selectedFile && (
            <View style={styles.selectedFileContainer}>
              <MaterialIcons name="insert-drive-file" size={24} color="#27ae60" />
              <View style={styles.fileInfo}>
                <Text style={styles.fileName}>{selectedFile.name}</Text>
                <Text style={styles.fileSize}>
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </Text>
              </View>
              <TouchableOpacity
                onPress={() => setSelectedFile(null)}
                disabled={uploading}
              >
                <MaterialIcons name="close" size={24} color="#e74c3c" />
              </TouchableOpacity>
            </View>
          )}

          {/* 上传按钮 */}
          <TouchableOpacity
            style={[
              styles.uploadButton,
              (!selectedFile || uploading) && styles.uploadButtonDisabled,
            ]}
            onPress={handleUpload}
            disabled={!selectedFile || uploading}
          >
            {uploading ? (
              <>
                <ActivityIndicator size="small" color="#fff" />
                <Text style={styles.uploadButtonText}>上传中...</Text>
              </>
            ) : (
              <>
                <MaterialIcons name="cloud-upload" size={24} color="#fff" />
                <Text style={styles.uploadButtonText}>上传并解析</Text>
              </>
            )}
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f6fa',
  },
  content: {
    padding: 15,
  },
  infoCard: {
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
  infoHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginLeft: 10,
  },
  infoText: {
    fontSize: 14,
    color: '#7f8c8d',
    marginBottom: 10,
  },
  formatList: {
    backgroundColor: '#ecf0f1',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
  },
  formatItem: {
    fontSize: 13,
    color: '#2c3e50',
    marginBottom: 8,
    lineHeight: 20,
  },
  infoNote: {
    fontSize: 12,
    color: '#95a5a6',
    fontStyle: 'italic',
  },
  uploadCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  selectButton: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
    borderWidth: 2,
    borderColor: '#e74c3c',
    borderStyle: 'dashed',
    borderRadius: 12,
    backgroundColor: '#fff5f5',
  },
  selectButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    marginTop: 10,
  },
  selectButtonHint: {
    fontSize: 12,
    color: '#95a5a6',
    marginTop: 5,
  },
  selectedFileContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f9ff',
    borderRadius: 8,
    padding: 12,
    marginTop: 15,
    borderWidth: 1,
    borderColor: '#27ae60',
  },
  fileInfo: {
    flex: 1,
    marginLeft: 10,
  },
  fileName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 2,
  },
  fileSize: {
    fontSize: 12,
    color: '#7f8c8d',
  },
  uploadButton: {
    backgroundColor: '#e74c3c',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    borderRadius: 12,
    marginTop: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  uploadButtonDisabled: {
    backgroundColor: '#bdc3c7',
  },
  uploadButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10,
  },
});
