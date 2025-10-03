import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { Invoice, InvoiceStatus } from '../types/Invoice';
import LoadingSpinner from '../components/LoadingSpinner';

interface Props {
  navigation: StackNavigationProp<any>;
}

export default function InvoiceListScreen({ navigation }: Props) {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      setIsLoading(true);
      // TODO: Implement API call to get invoices
      // Mock data for now
      setInvoices([
        {
          id: '1',
          invoiceNumber: 'INV-2024-001',
          supplierName: 'Acme Corp',
          totalAmount: 1000.00,
          currency: 'USD',
          status: InvoiceStatus.PENDING_APPROVAL,
          invoiceDate: '2024-01-15',
          createdAt: '2024-01-15T10:30:00Z',
          updatedAt: '2024-01-15T10:30:00Z',
          companyId: 'company-1',
          createdBy: 'user-1',
          taxAmount: 80.00,
          taxRate: 0.08,
          subtotal: 920.00,
          totalWithTax: 1000.00,
          invoiceType: 'invoice' as any,
        },
      ]);
    } catch (error) {
      console.error('Failed to load invoices:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadInvoices();
    setRefreshing(false);
  };

  const getStatusColor = (status: InvoiceStatus): string => {
    switch (status) {
      case InvoiceStatus.PENDING_APPROVAL:
        return '#f59e0b';
      case InvoiceStatus.APPROVED:
        return '#10b981';
      case InvoiceStatus.REJECTED:
        return '#ef4444';
      case InvoiceStatus.POSTED_TO_ERP:
        return '#3b82f6';
      default:
        return '#6b7280';
    }
  };

  const getStatusIcon = (status: InvoiceStatus): string => {
    switch (status) {
      case InvoiceStatus.PENDING_APPROVAL:
        return '⏳';
      case InvoiceStatus.APPROVED:
        return '✅';
      case InvoiceStatus.REJECTED:
        return '❌';
      case InvoiceStatus.POSTED_TO_ERP:
        return '📤';
      default:
        return '📄';
    }
  };

  const renderInvoice = ({ item }: { item: Invoice }) => (
    <TouchableOpacity
      style={styles.invoiceCard}
      onPress={() => navigation.navigate('InvoiceDetail', { invoice: item })}
    >
      <View style={styles.invoiceHeader}>
        <Text style={styles.invoiceNumber}>{item.invoiceNumber}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={styles.statusIcon}>{getStatusIcon(item.status)}</Text>
          <Text style={styles.statusText}>{item.status.replace('_', ' ')}</Text>
        </View>
      </View>
      
      <Text style={styles.supplierName}>{item.supplierName}</Text>
      
      <View style={styles.invoiceDetails}>
        <Text style={styles.amount}>
          {item.currency} {item.totalAmount.toFixed(2)}
        </Text>
        <Text style={styles.date}>{item.invoiceDate}</Text>
      </View>
    </TouchableOpacity>
  );

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <LoadingSpinner size="large" text="Loading invoices..." />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={invoices}
        renderItem={renderInvoice}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyIcon}>📄</Text>
            <Text style={styles.emptyTitle}>No invoices found</Text>
            <Text style={styles.emptySubtitle}>
              Start by scanning an invoice or creating one manually
            </Text>
          </View>
        }
      />
    </View>
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
  listContainer: {
    padding: 16,
  },
  invoiceCard: {
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  invoiceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  invoiceNumber: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusIcon: {
    fontSize: 12,
    marginRight: 4,
  },
  statusText: {
    fontSize: 12,
    color: '#ffffff',
    fontWeight: '500',
    textTransform: 'capitalize',
  },
  supplierName: {
    fontSize: 14,
    color: '#9ca3af',
    marginBottom: 8,
  },
  invoiceDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  amount: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  date: {
    fontSize: 14,
    color: '#9ca3af',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 48,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#9ca3af',
    textAlign: 'center',
    paddingHorizontal: 32,
  },
});
