import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { User } from '../types/User';
import { Invoice, InvoiceStatus } from '../types/Invoice';
import LoadingSpinner from '../components/LoadingSpinner';

interface Props {
  navigation: StackNavigationProp<any>;
  user?: User;
}

export default function DashboardScreen({ navigation, user }: Props) {
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    totalInvoices: 0,
    pendingApproval: 0,
    approvedToday: 0,
    rejectedToday: 0,
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      // TODO: Implement API calls to get dashboard data
      // For now, using mock data
      setStats({
        totalInvoices: 156,
        pendingApproval: 12,
        approvedToday: 8,
        rejectedToday: 2,
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const StatCard = ({ title, value, color, onPress }: {
    title: string;
    value: number;
    color: string;
    onPress?: () => void;
  }) => (
    <TouchableOpacity 
      style={[styles.statCard, { borderLeftColor: color }]} 
      onPress={onPress}
      disabled={!onPress}
    >
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statTitle}>{title}</Text>
    </TouchableOpacity>
  );

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <LoadingSpinner size="large" text="Loading dashboard..." />
      </View>
    );
  }

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.greeting}>
          Welcome back, {user?.firstName || 'User'}!
        </Text>
        <Text style={styles.subtitle}>Here's your invoice overview</Text>
      </View>

      <View style={styles.statsGrid}>
        <StatCard
          title="Total Invoices"
          value={stats.totalInvoices}
          color="#3b82f6"
          onPress={() => navigation.navigate('Invoices')}
        />
        <StatCard
          title="Pending Approval"
          value={stats.pendingApproval}
          color="#f59e0b"
          onPress={() => navigation.navigate('Invoices', { filter: 'pending' })}
        />
        <StatCard
          title="Approved Today"
          value={stats.approvedToday}
          color="#10b981"
        />
        <StatCard
          title="Rejected Today"
          value={stats.rejectedToday}
          color="#ef4444"
        />
      </View>

      <View style={styles.quickActions}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        
        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => navigation.navigate('Camera')}
        >
          <Text style={styles.actionIcon}>📷</Text>
          <Text style={styles.actionText}>Scan Invoice</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => navigation.navigate('Invoices')}
        >
          <Text style={styles.actionIcon}>📄</Text>
          <Text style={styles.actionText}>View All Invoices</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => navigation.navigate('OfflineSync')}
        >
          <Text style={styles.actionIcon}>🔄</Text>
          <Text style={styles.actionText}>Sync Offline Data</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.recentActivity}>
        <Text style={styles.sectionTitle}>Recent Activity</Text>
        <View style={styles.activityItem}>
          <Text style={styles.activityIcon}>✅</Text>
          <View style={styles.activityContent}>
            <Text style={styles.activityText}>Invoice INV-2024-001 approved</Text>
            <Text style={styles.activityTime}>2 minutes ago</Text>
          </View>
        </View>
        <View style={styles.activityItem}>
          <Text style={styles.activityIcon}>📷</Text>
          <View style={styles.activityContent}>
            <Text style={styles.activityText}>New invoice scanned</Text>
            <Text style={styles.activityTime}>15 minutes ago</Text>
          </View>
        </View>
        <View style={styles.activityItem}>
          <Text style={styles.activityIcon}>❌</Text>
          <View style={styles.activityContent}>
            <Text style={styles.activityText}>Invoice INV-2024-002 rejected</Text>
            <Text style={styles.activityTime}>1 hour ago</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#111827',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#111827',
  },
  header: {
    padding: 20,
    paddingBottom: 16,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#9ca3af',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  statCard: {
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    marginRight: 12,
    width: '45%',
    borderLeftWidth: 4,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  statTitle: {
    fontSize: 14,
    color: '#9ca3af',
  },
  quickActions: {
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 16,
  },
  actionButton: {
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  actionIcon: {
    fontSize: 24,
    marginRight: 16,
  },
  actionText: {
    fontSize: 16,
    color: '#ffffff',
    fontWeight: '500',
  },
  recentActivity: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  activityIcon: {
    fontSize: 20,
    marginRight: 16,
  },
  activityContent: {
    flex: 1,
  },
  activityText: {
    fontSize: 16,
    color: '#ffffff',
    marginBottom: 4,
  },
  activityTime: {
    fontSize: 14,
    color: '#9ca3af',
  },
});
