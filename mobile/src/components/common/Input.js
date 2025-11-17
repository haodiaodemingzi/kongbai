import React, { useState } from 'react';
import {
  View,
  TextInput,
  StyleSheet,
  Text
} from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { colors } from '../../styles/colors';
import { spacing } from '../../styles/spacing';

export default function Input({
  placeholder,
  value,
  onChangeText,
  icon,
  secureTextEntry = false,
  keyboardType = 'default',
  editable = true,
  label,
  error,
  style = {}
}) {
  const [focused, setFocused] = useState(false);

  return (
    <View style={style}>
      {label && (
        <Text style={styles.label}>{label}</Text>
      )}
      <View
        style={[
          styles.container,
          focused && styles.containerFocused,
          error && styles.containerError
        ]}
      >
        {icon && (
          <MaterialCommunityIcons
            name={icon}
            size={20}
            color={focused ? colors.primary : colors.neutral[400]}
            style={styles.icon}
          />
        )}
        <TextInput
          style={styles.input}
          placeholder={placeholder}
          placeholderTextColor={colors.neutral[300]}
          value={value}
          onChangeText={onChangeText}
          secureTextEntry={secureTextEntry}
          keyboardType={keyboardType}
          editable={editable}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
        />
      </View>
      {error && (
        <Text style={styles.errorText}>{error}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.neutral[700],
    marginBottom: spacing.sm
  },
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: spacing.md,
    backgroundColor: colors.background,
    height: 48
  },
  containerFocused: {
    borderColor: colors.primary,
    borderWidth: 2
  },
  containerError: {
    borderColor: colors.error
  },
  icon: {
    marginRight: spacing.md
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: colors.neutral[900],
    padding: 0
  },
  errorText: {
    fontSize: 12,
    color: colors.error,
    marginTop: spacing.sm
  }
});
