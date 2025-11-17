import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';

export default function App() {
  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* 顶部标题 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>战斗统计</Text>
        <Text style={styles.headerSubtitle}>Battle Stats</Text>
      </View>

      {/* 主要内容 */}
      <ScrollView style={styles.content}>
        {/* 统计卡片 */}
        <View style={styles.statsRow}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>1,234</Text>
            <Text style={styles.statLabel}>总击杀</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>567</Text>
            <Text style={styles.statLabel}>总死亡</Text>
          </View>
        </View>

        <View style={styles.statsRow}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>3,145</Text>
            <Text style={styles.statLabel}>总得分</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>2.18</Text>
            <Text style={styles.statLabel}>K/D 比</Text>
          </View>
        </View>

        {/* 势力统计 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>势力统计</Text>
          
          <View style={styles.factionCard}>
            <View style={[styles.factionBar, { backgroundColor: '#e74c3c' }]} />
            <Text style={styles.factionName}>梵天</Text>
            <Text style={styles.factionScore}>1,050</Text>
          </View>

          <View style={styles.factionCard}>
            <View style={[styles.factionBar, { backgroundColor: '#3498db' }]} />
            <Text style={styles.factionName}>比湿奴</Text>
            <Text style={styles.factionScore}>980</Text>
          </View>

          <View style={styles.factionCard}>
            <View style={[styles.factionBar, { backgroundColor: '#9b59b6' }]} />
            <Text style={styles.factionName}>湿婆</Text>
            <Text style={styles.factionScore}>1,115</Text>
          </View>
        </View>

        {/* 操作按钮 */}
        <TouchableOpacity style={styles.button}>
          <Text style={styles.buttonText}>查看排名</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.button, styles.buttonSecondary]}>
          <Text style={styles.buttonTextSecondary}>上传战斗记录</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f6fa',
  },
  header: {
    backgroundColor: '#2c3e50',
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#bdc3c7',
    marginTop: 5,
  },
  content: {
    flex: 1,
    padding: 15,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginHorizontal: 5,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  statLabel: {
    fontSize: 14,
    color: '#7f8c8d',
    marginTop: 5,
  },
  section: {
    marginTop: 10,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
  },
  factionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  factionBar: {
    width: 4,
    height: 40,
    borderRadius: 2,
    marginRight: 15,
  },
  factionName: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
  },
  factionScore: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#3498db',
  },
  button: {
    backgroundColor: '#3498db',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginBottom: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonSecondary: {
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#3498db',
  },
  buttonTextSecondary: {
    color: '#3498db',
    fontSize: 16,
    fontWeight: '600',
  },
});
