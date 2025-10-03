import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { Invoice, SyncStatus } from '../types/Invoice';
import { offlineSyncService } from '../services/OfflineSyncService';
import { pushNotificationService } from '../services/PushNotificationService';

interface OfflineInvoicesScreenProps {
  navigation: any;
}

export const OfflineInvoicesScreen: React.FC<OfflineInvoicesScreenProps> = ({ navigation }) => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [pendingSyncCount, setPendingSyncCount] = useState(0);
  const [lastSyncTime, setLastSyncTime] = useState<number | null>(null);

  useFocusEffect(
    useCallback(() => {
      loadOfflineInvoices();
    }, [])
  );

  const loadOfflineInvoices = async () => {
    try {
      setIsLoading(true);
      const offlineInvoices = await offlineSyncService.getOfflineInvoices();
      const pendingCount = await offlineSyncService.getPendingSyncCount();
      const lastSync = await offlineSyncService.getLastSyncTime();
      
      setInvoices(offlineInvoices);
      setPendingSyncCount(pendingCount);
      setLastSyncTime(lastSync);
    } catch (error) {
      console.error('Failed to load offline invoices:', error);
      Alert.alert('Error', 'Failed to load offline invoices');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadOfflineInvoices();
    setIsRefreshing(false);
  };

  const handleSyncNow = async () => {
    try {
      await offlineSyncService.syncOfflineData();
      await loadOfflineInvoices();
      
      await pushNotificationService.sendLocalNotification(
        'Sync Complete',
        'All offline invoices have been synced successfully',
        { type: 'sync_completed' }
      );
      
      Alert.alert('Success', 'Offline data synced successfully');
    } catch (error) {
      console.error('Sync failed:', error);
      
      await pushNotificationService.sendLocalNotification(
        'Sync Failed',
        'Failed to sync offline invoices',
        { type: 'sync_failed', message: error instanceof Error ? error.message : 'Unknown error' }
      );
      
      Alert.alert('Sync Failed', 'Failed to sync offline data');
    }
  };

  const handleInvoicePress = (invoice: Invoice) => {
    navigation.navigate('InvoiceDetails', { invoice });
  };

  const handleDeleteInvoice = async (invoice: Invoice) => {
    Alert.alert(
      'Delete Invoice',
      `Are you sure you want to delete invoice ${invoice.invoiceNumber}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await offlineSyncService.addAction('DELETE', invoice);
              await loadOfflineInvoices();
              Alert.alert('Success', 'Invoice deleted successfully');
            } catch (error) {
              Alert.alert('Error', 'Failed to delete invoice');
            }
          },
        },
      ]
    );
  };

  const getSyncStatusIcon = (status: SyncStatus) => {
    switch (status) {
      case SyncStatus.SYNCED:
        return <Ionicons name="checkmark-circle" size={20} color="#34C759" />;
      case SyncStatus.PENDING:
        return <Ionicons name="time" size={20} color="#FF9500" />;
      case SyncStatus.FAILED:
        return <Ionicons name="close-circle" size={20} color="#FF3B30" />;
      default:
        return <Ionicons name="help-circle" size={20} color="#8E8E93" />;
    }
  };

  const getSyncStatusText = (status: SyncStatus) => {
    switch (status) {
      case SyncStatus.SYNCED:
        return 'Synced';
      case SyncStatus.PENDING:
        return 'Pending';
      case SyncStatus.FAILED:
        return 'Failed';
      default:
        return 'Unknown';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatAmount = (amount: number, currency: string) => {
    return `${currency} ${amount.toFixed(2)}`;
  };

  const renderInvoiceItem = ({ item }: { item: Invoice }) => (
    <TouchableOpacity
      style={styles.invoiceItem}
      onPress={() => handleInvoicePress(item)}
    >
      <View style={styles.invoiceHeader}>
        <Text style={styles.invoiceNumber}>{item.invoiceNumber}</Text>
        <View style={styles.syncStatus}>
          {getSyncStatusIcon(item.syncStatus)}
          <Text style={styles.syncStatusText}>{getSyncStatusText(item.syncStatus)}</Text>
        </View>
      </View>
      
      <Text style={styles.vendorName}>{item.vendorName}</Text>
      
      <View style={styles.invoiceDetails}>
        <Text style={styles.amount}>{formatAmount(item.amount, item.currency)}</Text>
        <Text style={styles.date}>{formatDate(item.invoiceDate)}</Text>
      </View>
      
      {item.isOffline && (
        <View style={styles.offlineIndicator}>
          <Ionicons name="cloud-offline" size={16} color="#FF9500" />
          <Text style={styles.offlineText}>Offline</Text>
        </View>
      )}
      
      <TouchableOpacity
        style={styles.deleteButton}
        onPress={() => handleDeleteInvoice(item)}
      >
        <Ionicons name="trash" size={20} color="#FF3B30" />
      </TouchableOpacity>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Ionicons name="document-outline" size={64} color="#8E8E93" />
      <Text style={styles.emptyTitle}>No Offline Invoices</Text>
      <Text style={styles.emptyMessage}>
        Capture invoices to see them here when offline
      </Text>
    </View>
  );

  const renderHeader = () => (
    <View style={styles.header}>
      <View style={styles.headerTop}>
        <Text style={styles.title}>Offline Invoices</Text>
        {pendingSyncCount > 0 && (
          <TouchableOpacity style={styles.syncButton} onPress={handleSyncNow}>
            <Ionicons name="sync" size={20} color="#fff" />
            <Text style={styles.syncText}>Sync ({pendingSyncCount})</Text>
          </TouchableOpacity>
        )}
      </View>
      
      {lastSyncTime && (
        <Text style={styles.lastSyncText}>
          Last sync: {new Date(lastSyncTime).toLocaleString()}
        </Text>
      )}
    </View>
  );

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading offline invoices...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={invoices}
        renderItem={renderInvoiceItem}
        keyExtractor={(item) => item.id}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={renderEmptyState}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
        }
        contentContainerStyle={styles.listContainer}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  listContainer: {
    flexGrow: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  syncButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#007AFF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  syncText: {
    color: '#fff',
    marginLeft: 4,
    fontWeight: 'bold',
  },
  lastSyncText: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  invoiceItem: {
    backgroundColor: '#fff',
    marginHorizontal: 20,
    marginVertical: 5,
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  invoiceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  invoiceNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  syncStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  syncStatusText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  vendorName: {
    fontSize: 16,
    color: '#666',
    marginBottom: 10,
  },
  invoiceDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  amount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  date: {
    fontSize: 14,
    color: '#666',
  },
  offlineIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
  },
  offlineText: {
    fontSize: 12,
    color: '#FF9500',
    marginLeft: 4,
  },
  deleteButton: {
    position: 'absolute',
    top: 15,
    right: 15,
    padding: 5,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 16,
  },
  emptyMessage: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
  },
});








