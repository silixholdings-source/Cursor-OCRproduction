import AsyncStorage from '@react-native-async-storage/async-storage';
import { Invoice, SyncStatus } from '../types/Invoice';
import { authService } from './AuthService';

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1' 
  : 'https://api.ai-erp-saas.com/api/v1';

interface OfflineAction {
  id: string;
  type: 'CREATE' | 'UPDATE' | 'DELETE' | 'APPROVE' | 'REJECT';
  data: any;
  timestamp: number;
  retryCount: number;
}

class OfflineSyncService {
  private static instance: OfflineSyncService;
  private isInitialized = false;
  private syncInProgress = false;

  static getInstance(): OfflineSyncService {
    if (!OfflineSyncService.instance) {
      OfflineSyncService.instance = new OfflineSyncService();
    }
    return OfflineSyncService.instance;
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Initialize offline storage
      await this.initializeOfflineStorage();
      this.isInitialized = true;
      console.log('OfflineSyncService initialized');
    } catch (error) {
      console.error('Failed to initialize OfflineSyncService:', error);
      throw error;
    }
  }

  private async initializeOfflineStorage(): Promise<void> {
    // Create offline storage structure if it doesn't exist
    const offlineData = await AsyncStorage.getItem('offline_data');
    if (!offlineData) {
      await AsyncStorage.setItem('offline_data', JSON.stringify({
        invoices: [],
        actions: [],
        lastSync: null,
      }));
    }
  }

  async saveInvoiceOffline(invoice: Invoice): Promise<void> {
    try {
      const offlineData = await this.getOfflineData();
      
      // Add or update invoice in offline storage
      const existingIndex = offlineData.invoices.findIndex((i: Invoice) => i.id === invoice.id);
      if (existingIndex >= 0) {
        offlineData.invoices[existingIndex] = { ...invoice, isOffline: true, syncStatus: SyncStatus.PENDING };
      } else {
        offlineData.invoices.push({ ...invoice, isOffline: true, syncStatus: SyncStatus.PENDING });
      }

      // Add action to queue
      const action: OfflineAction = {
        id: `action_${Date.now()}_${Math.random()}`,
        type: existingIndex >= 0 ? 'UPDATE' : 'CREATE',
        data: invoice,
        timestamp: Date.now(),
        retryCount: 0,
      };
      offlineData.actions.push(action);

      await this.saveOfflineData(offlineData);
      console.log('Invoice saved offline:', invoice.id);
    } catch (error) {
      console.error('Failed to save invoice offline:', error);
      throw error;
    }
  }

  async getOfflineInvoices(): Promise<Invoice[]> {
    try {
      const offlineData = await this.getOfflineData();
      return offlineData.invoices || [];
    } catch (error) {
      console.error('Failed to get offline invoices:', error);
      return [];
    }
  }

  async getPendingSyncCount(): Promise<number> {
    try {
      const offlineData = await this.getOfflineData();
      return offlineData.actions?.length || 0;
    } catch (error) {
      console.error('Failed to get pending sync count:', error);
      return 0;
    }
  }

  async syncOfflineData(): Promise<void> {
    if (this.syncInProgress) {
      console.log('Sync already in progress');
      return;
    }

    this.syncInProgress = true;

    try {
      const offlineData = await this.getOfflineData();
      const actions = offlineData.actions || [];

      if (actions.length === 0) {
        console.log('No offline actions to sync');
        return;
      }

      console.log(`Syncing ${actions.length} offline actions...`);

      for (const action of actions) {
        try {
          await this.executeAction(action);
          await this.removeAction(action.id);
        } catch (error) {
          console.error(`Failed to execute action ${action.id}:`, error);
          action.retryCount++;
          
          if (action.retryCount >= 3) {
            console.error(`Action ${action.id} failed after 3 retries, removing from queue`);
            await this.removeAction(action.id);
          } else {
            await this.updateAction(action);
          }
        }
      }

      // Update last sync timestamp
      offlineData.lastSync = Date.now();
      await this.saveOfflineData(offlineData);

      console.log('Offline sync completed');
    } catch (error) {
      console.error('Offline sync failed:', error);
      throw error;
    } finally {
      this.syncInProgress = false;
    }
  }

  private async executeAction(action: OfflineAction): Promise<void> {
    const headers = authService.getAuthHeaders();

    switch (action.type) {
      case 'CREATE':
        await fetch(`${API_BASE_URL}/invoices`, {
          method: 'POST',
          headers,
          body: JSON.stringify(action.data),
        });
        break;

      case 'UPDATE':
        await fetch(`${API_BASE_URL}/invoices/${action.data.id}`, {
          method: 'PUT',
          headers,
          body: JSON.stringify(action.data),
        });
        break;

      case 'DELETE':
        await fetch(`${API_BASE_URL}/invoices/${action.data.id}`, {
          method: 'DELETE',
          headers,
        });
        break;

      case 'APPROVE':
        await fetch(`${API_BASE_URL}/invoices/${action.data.id}/approve`, {
          method: 'POST',
          headers,
        });
        break;

      case 'REJECT':
        await fetch(`${API_BASE_URL}/invoices/${action.data.id}/reject`, {
          method: 'POST',
          headers,
          body: JSON.stringify({ reason: action.data.reason }),
        });
        break;

      default:
        throw new Error(`Unknown action type: ${action.type}`);
    }
  }

  async addAction(type: OfflineAction['type'], data: any): Promise<void> {
    try {
      const offlineData = await this.getOfflineData();
      
      const action: OfflineAction = {
        id: `action_${Date.now()}_${Math.random()}`,
        type,
        data,
        timestamp: Date.now(),
        retryCount: 0,
      };
      
      offlineData.actions.push(action);
      await this.saveOfflineData(offlineData);
    } catch (error) {
      console.error('Failed to add action:', error);
      throw error;
    }
  }

  private async getOfflineData(): Promise<any> {
    const data = await AsyncStorage.getItem('offline_data');
    return data ? JSON.parse(data) : { invoices: [], actions: [], lastSync: null };
  }

  private async saveOfflineData(data: any): Promise<void> {
    await AsyncStorage.setItem('offline_data', JSON.stringify(data));
  }

  private async removeAction(actionId: string): Promise<void> {
    const offlineData = await this.getOfflineData();
    offlineData.actions = offlineData.actions.filter((action: OfflineAction) => action.id !== actionId);
    await this.saveOfflineData(offlineData);
  }

  private async updateAction(action: OfflineAction): Promise<void> {
    const offlineData = await this.getOfflineData();
    const index = offlineData.actions.findIndex((a: OfflineAction) => a.id === action.id);
    if (index >= 0) {
      offlineData.actions[index] = action;
      await this.saveOfflineData(offlineData);
    }
  }

  async clearOfflineData(): Promise<void> {
    await AsyncStorage.removeItem('offline_data');
    await this.initializeOfflineStorage();
  }

  async getLastSyncTime(): Promise<number | null> {
    try {
      const offlineData = await this.getOfflineData();
      return offlineData.lastSync;
    } catch (error) {
      console.error('Failed to get last sync time:', error);
      return null;
    }
  }
}

export const offlineSyncService = OfflineSyncService.getInstance();
