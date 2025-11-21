import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Animated,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons } from '@expo/vector-icons';
import { login, getRememberedUsername, getRememberedPassword, getRememberSettings } from '../services/api';

export default function LoginScreen({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [rememberUsername, setRememberUsername] = useState(false);
  const [rememberPassword, setRememberPassword] = useState(false);
  const [fadeAnim] = useState(new Animated.Value(0));

  useEffect(() => {
    // 加载动画
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 1000,
      useNativeDriver: true,
    }).start();
    
    // 加载记住的用户名
    loadRememberedUsername();
  }, []);

  // 加载记住的用户名和密码
  const loadRememberedUsername = async () => {
    try {
      const savedUsername = await getRememberedUsername();
      const savedPassword = await getRememberedPassword();
      const settings = await getRememberSettings();
      
      if (savedUsername && settings.rememberUsername) {
        setUsername(savedUsername);
        setRememberUsername(true);
      }
      
      if (savedPassword && settings.rememberPassword) {
        setPassword(savedPassword);
        setRememberPassword(true);
      }
    } catch (error) {
      console.error('加载用户名失败:', error);
    }
  };

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('错误', '请输入用户名和密码');
      return;
    }

    setLoading(true);
    try {
      const result = await login(username, password, rememberUsername, rememberPassword);

      if (result.success) {
        // 登录成功，添加淡出动画后进入主界面
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }).start(() => {
          onLoginSuccess(result.user, result.token);
        });
      } else {
        Alert.alert('登录失败', result.message || '用户名或密码错误');
      }
    } catch (error) {
      console.error('登录失败:', error);
      Alert.alert('登录失败', '网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient
      colors={['#e74c3c', '#c0392b', '#e74c3c']}
      style={styles.container}
    >
      <KeyboardAvoidingView
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <Animated.View style={[styles.content, { opacity: fadeAnim }]}>
          {/* Logo 区域 */}
          <View style={styles.logoContainer}>
            <View style={styles.logoCircle}>
              <MaterialIcons name="sports-martial-arts" size={60} color="#fff" />
            </View>
            <Text style={styles.title}>战斗统计</Text>
            <Text style={styles.subtitle}>Battle Stats</Text>
          </View>

          {/* 表单区域 */}
          <View style={styles.formContainer}>
            <View style={styles.inputContainer}>
              <View style={styles.inputWrapper}>
                <MaterialIcons name="person" size={20} color="#667eea" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="请输入用户名"
                  placeholderTextColor="#999"
                  value={username}
                  onChangeText={setUsername}
                  autoCapitalize="none"
                  editable={!loading}
                />
              </View>
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.inputWrapper}>
                <MaterialIcons name="lock" size={20} color="#667eea" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="请输入密码"
                  placeholderTextColor="#999"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  editable={!loading}
                />
              </View>
            </View>

            {/* 记住账号复选框 */}
            <TouchableOpacity
              style={styles.checkboxContainer}
              onPress={() => setRememberUsername(!rememberUsername)}
              disabled={loading}
            >
              <View style={[styles.checkbox, rememberUsername && styles.checkboxChecked]}>
                {rememberUsername && (
                  <MaterialIcons name="check" size={16} color="#fff" />
                )}
              </View>
              <Text style={styles.checkboxLabel}>记住账号</Text>
            </TouchableOpacity>

            {/* 记住密码复选框 */}
            <TouchableOpacity
              style={styles.checkboxContainer}
              onPress={() => setRememberPassword(!rememberPassword)}
              disabled={loading}
            >
              <View style={[styles.checkbox, rememberPassword && styles.checkboxChecked]}>
                {rememberPassword && (
                  <MaterialIcons name="check" size={16} color="#fff" />
                )}
              </View>
              <Text style={styles.checkboxLabel}>记住密码</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.loginButton, loading && styles.loginButtonDisabled]}
              onPress={handleLogin}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <View style={styles.loginButtonContent}>
                  <MaterialIcons name="login" size={20} color="#fff" style={{ marginRight: 8 }} />
                  <Text style={styles.loginButtonText}>登录</Text>
                </View>
              )}
            </TouchableOpacity>

            {/* 提示信息 */}
            <View style={styles.hintContainer}>
              <MaterialIcons name="info-outline" size={16} color="#667eea" />
              <Text style={styles.hintText}>首次使用请联系管理员获取账号</Text>
            </View>
          </View>
        </Animated.View>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    padding: 30,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 60,
  },
  logoCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.9)',
    letterSpacing: 2,
  },
  formContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 20,
    padding: 25,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 10,
  },
  inputContainer: {
    marginBottom: 20,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#e1e8ed',
    paddingHorizontal: 15,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    padding: 15,
    fontSize: 16,
    color: '#2c3e50',
  },
  loginButton: {
    backgroundColor: '#e74c3c',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 10,
    shadowColor: '#667eea',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 6,
  },
  loginButtonDisabled: {
    backgroundColor: '#95a5a6',
    shadowOpacity: 0.2,
  },
  loginButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  loginButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  hintContainer: {
    marginTop: 20,
    padding: 15,
    backgroundColor: 'rgba(102, 126, 234, 0.1)',
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  hintText: {
    fontSize: 13,
    color: '#667eea',
    marginLeft: 8,
    fontWeight: '500',
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 15,
    marginBottom: 5,
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: '#667eea',
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  checkboxChecked: {
    backgroundColor: '#667eea',
    borderColor: '#667eea',
  },
  checkboxLabel: {
    fontSize: 14,
    color: '#2c3e50',
    fontWeight: '500',
  },
});
