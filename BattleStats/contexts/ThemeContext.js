import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { THEMES, getThemeColors } from '../themes/theme';

const ThemeContext = createContext();

const THEME_STORAGE_KEY = '@battle_stats_theme';

export const ThemeProvider = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState(THEMES.RED);
  const [colors, setColors] = useState(getThemeColors(THEMES.RED));
  const [loading, setLoading] = useState(true);

  // 加载保存的主题
  useEffect(() => {
    loadTheme();
  }, []);

  const loadTheme = async () => {
    try {
      const savedTheme = await AsyncStorage.getItem(THEME_STORAGE_KEY);
      if (savedTheme) {
        setCurrentTheme(savedTheme);
        setColors(getThemeColors(savedTheme));
      }
    } catch (error) {
      console.error('加载主题失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const changeTheme = async (theme) => {
    try {
      await AsyncStorage.setItem(THEME_STORAGE_KEY, theme);
      setCurrentTheme(theme);
      setColors(getThemeColors(theme));
    } catch (error) {
      console.error('保存主题失败:', error);
    }
  };

  return (
    <ThemeContext.Provider value={{ currentTheme, colors, changeTheme, loading }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
