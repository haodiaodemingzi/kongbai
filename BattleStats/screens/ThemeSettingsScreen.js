import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { THEMES } from '../themes/theme';

export default function ThemeSettingsScreen({ navigation }) {
  const { currentTheme, colors, changeTheme } = useTheme();

  const themes = [
    { key: THEMES.RED, name: '热情红', icon: 'favorite', color: '#e74c3c' },
    { key: THEMES.BLUE, name: '科技蓝', icon: 'star', color: '#3498db' },
    { key: THEMES.BLACK, name: '经典黑', icon: 'dark-mode', color: '#2c3e50' },
    { key: THEMES.WHITE, name: '简约白', icon: 'light-mode', color: '#ecf0f1' },
    { key: THEMES.GREEN, name: '翡翠绿', icon: 'eco', color: '#1cb74d' },
  ];

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]}>
      <Text style={[styles.description, { color: colors.textSecondary }]}>
        选择您喜欢的主题颜色，主题将应用到整个应用
      </Text>

      <View style={styles.themeContainer}>
        {themes.map((theme) => (
          <TouchableOpacity
            key={theme.key}
            style={[
              styles.themeOption,
              { backgroundColor: colors.cardBackground, borderColor: colors.border },
              currentTheme === theme.key && { borderColor: theme.color, borderWidth: 2 }
            ]}
            onPress={() => changeTheme(theme.key)}
          >
            <View style={[styles.themeColor, { backgroundColor: theme.color }]}>
              <MaterialIcons 
                name={theme.icon} 
                size={24} 
                color={theme.key === THEMES.WHITE ? '#3498db' : '#fff'} 
              />
            </View>
            <Text style={[styles.themeName, { color: colors.text }]}>{theme.name}</Text>
            {currentTheme === theme.key && (
              <MaterialIcons name="check-circle" size={20} color={theme.color} />
            )}
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  description: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 20,
  },
  themeContainer: {
    gap: 12,
  },
  themeOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  themeColor: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  themeName: {
    flex: 1,
    fontSize: 16,
    fontWeight: '500',
  },
});
