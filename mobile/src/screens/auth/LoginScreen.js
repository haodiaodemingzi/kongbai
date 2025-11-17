import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ActivityIndicator
} from 'react-native';
import { useDispatch } from 'react-redux';
import LinearGradient from 'react-native-linear-gradient';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import Toast from 'react-native-toast-message';
import { login } from '../../store/reducers/authReducer';
import { colors } from '../../styles/colors';
import { spacing } from '../../styles/spacing';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';

export default function LoginScreen({ navigation }) {
  const dispatch = useDispatch();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async () => {
    if (!username.trim()) {
      Toast.show({
        type: 'error',
        text1: '错误',
        text2: '请输入用户名'
      });
      return;
    }

    if (!password.trim()) {
      Toast.show({
        type: 'error',
        text1: '错误',
        text2: '请输入密码'
      });
      return;
    }

    setLoading(true);
    try {
      await dispatch(login(username, password));
    } catch (error) {
      Toast.show({
        type: 'error',
        text1: '登录失败',
        text2: error.message || '请检查用户名和密码'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient
      colors={[colors.primary, colors.secondary]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.container}
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoid}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Logo 区域 */}
          <View style={styles.logoContainer}>
            <View style={styles.logoCircle}>
              <MaterialCommunityIcons
                name="trophy"
                size={60}
                color={colors.background}
              />
            </View>
            <Text style={styles.appName}>战斗统计</Text>
            <Text style={styles.appSubtitle}>Battle Stats</Text>
          </View>

          {/* 表单区域 */}
          <View style={styles.formContainer}>
            <Text style={styles.formTitle}>登录账户</Text>

            {/* 用户名输入 */}
            <Input
              placeholder="用户名或邮箱"
              value={username}
              onChangeText={setUsername}
              icon="account"
              editable={!loading}
              style={styles.input}
            />

            {/* 密码输入 */}
            <View style={styles.passwordContainer}>
              <Input
                placeholder="密码"
                value={password}
                onChangeText={setPassword}
                icon="lock"
                secureTextEntry={!showPassword}
                editable={!loading}
                style={styles.input}
              />
              <TouchableOpacity
                style={styles.eyeButton}
                onPress={() => setShowPassword(!showPassword)}
              >
                <MaterialCommunityIcons
                  name={showPassword ? 'eye' : 'eye-off'}
                  size={20}
                  color={colors.neutral[400]}
                />
              </TouchableOpacity>
            </View>

            {/* 登录按钮 */}
            <Button
              title={loading ? '登录中...' : '登 录'}
              onPress={handleLogin}
              variant="primary"
              size="large"
              loading={loading}
              disabled={loading}
              style={styles.loginButton}
            />

            {/* 链接区域 */}
            <View style={styles.linksContainer}>
              <TouchableOpacity>
                <Text style={styles.link}>忘记密码?</Text>
              </TouchableOpacity>
              <Text style={styles.separator}>|</Text>
              <TouchableOpacity onPress={() => navigation.navigate('Register')}>
                <Text style={styles.link}>立即注册</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* 底部提示 */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>
              首次使用? 请先注册账户
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background
  },
  keyboardAvoid: {
    flex: 1
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xl
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: spacing.xl * 2
  },
  logoCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.lg
  },
  appName: {
    fontSize: 32,
    fontWeight: '700',
    color: colors.background,
    marginBottom: spacing.sm
  },
  appSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.7)',
    letterSpacing: 2
  },
  formContainer: {
    backgroundColor: colors.background,
    borderRadius: 16,
    padding: spacing.xl,
    marginBottom: spacing.xl,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 5
  },
  formTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.neutral[900],
    marginBottom: spacing.xl
  },
  input: {
    marginBottom: spacing.lg
  },
  passwordContainer: {
    position: 'relative',
    marginBottom: spacing.lg
  },
  eyeButton: {
    position: 'absolute',
    right: spacing.lg,
    top: '50%',
    transform: [{ translateY: -10 }]
  },
  loginButton: {
    marginTop: spacing.lg
  },
  linksContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing.xl
  },
  link: {
    color: colors.primary,
    fontSize: 14,
    fontWeight: '500'
  },
  separator: {
    color: colors.neutral[300],
    marginHorizontal: spacing.md,
    fontSize: 14
  },
  footer: {
    alignItems: 'center',
    marginTop: spacing.xl
  },
  footerText: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: 12
  }
});
