import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

class NotificationService {
  private static instance: NotificationService;
  private expoPushToken: string | null = null;

  static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  async initialize(): Promise<void> {
    try {
      // Request permissions
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.log('Failed to get push token for push notification!');
        return;
      }

      // Get push token
      if (Device.isDevice) {
        const token = await Notifications.getExpoPushTokenAsync({
          projectId: 'your-expo-project-id', // Replace with actual project ID
        });
        this.expoPushToken = token.data;
        console.log('Expo push token:', this.expoPushToken);
        
        // Store token for later use
        await AsyncStorage.setItem('expo_push_token', this.expoPushToken);
      } else {
        console.log('Must use physical device for Push Notifications');
      }

      // Configure notification channel for Android
      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('default', {
          name: 'default',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#FF231F7C',
        });
      }
    } catch (error) {
      console.error('Failed to initialize notifications:', error);
    }
  }

  async registerForPushNotifications(): Promise<string | null> {
    try {
      if (!this.expoPushToken) {
        await this.initialize();
      }
      return this.expoPushToken;
    } catch (error) {
      console.error('Failed to register for push notifications:', error);
      return null;
    }
  }

  async sendLocalNotification(title: string, body: string, data?: any): Promise<void> {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
          sound: 'default',
        },
        trigger: null, // Send immediately
      });
    } catch (error) {
      console.error('Failed to send local notification:', error);
    }
  }

  async scheduleNotification(
    title: string, 
    body: string, 
    trigger: Notifications.NotificationTriggerInput,
    data?: any
  ): Promise<string> {
    try {
      const notificationId = await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
          sound: 'default',
        },
        trigger,
      });
      return notificationId;
    } catch (error) {
      console.error('Failed to schedule notification:', error);
      throw error;
    }
  }

  async cancelNotification(notificationId: string): Promise<void> {
    try {
      await Notifications.cancelScheduledNotificationAsync(notificationId);
    } catch (error) {
      console.error('Failed to cancel notification:', error);
    }
  }

  async cancelAllNotifications(): Promise<void> {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
    } catch (error) {
      console.error('Failed to cancel all notifications:', error);
    }
  }

  async getBadgeCount(): Promise<number> {
    try {
      return await Notifications.getBadgeCountAsync();
    } catch (error) {
      console.error('Failed to get badge count:', error);
      return 0;
    }
  }

  async setBadgeCount(count: number): Promise<void> {
    try {
      await Notifications.setBadgeCountAsync(count);
    } catch (error) {
      console.error('Failed to set badge count:', error);
    }
  }

  // Invoice-specific notification methods
  async notifyInvoiceApprovalRequired(invoiceId: string, invoiceNumber: string): Promise<void> {
    await this.sendLocalNotification(
      'Invoice Approval Required',
      `Invoice ${invoiceNumber} requires your approval`,
      {
        type: 'invoice_approval',
        invoiceId,
        invoiceNumber,
      }
    );
  }

  async notifyInvoiceApproved(invoiceId: string, invoiceNumber: string): Promise<void> {
    await this.sendLocalNotification(
      'Invoice Approved',
      `Invoice ${invoiceNumber} has been approved`,
      {
        type: 'invoice_approved',
        invoiceId,
        invoiceNumber,
      }
    );
  }

  async notifyInvoiceRejected(invoiceId: string, invoiceNumber: string, reason?: string): Promise<void> {
    await this.sendLocalNotification(
      'Invoice Rejected',
      `Invoice ${invoiceNumber} has been rejected${reason ? `: ${reason}` : ''}`,
      {
        type: 'invoice_rejected',
        invoiceId,
        invoiceNumber,
        reason,
      }
    );
  }

  async notifyTrialExpiring(daysLeft: number): Promise<void> {
    await this.sendLocalNotification(
      'Trial Expiring Soon',
      `Your trial expires in ${daysLeft} day${daysLeft === 1 ? '' : 's'}. Consider upgrading to continue using the app.`,
      {
        type: 'trial_reminder',
        daysLeft,
      }
    );
  }

  async notifySyncCompleted(syncedCount: number): Promise<void> {
    await this.sendLocalNotification(
      'Sync Completed',
      `${syncedCount} item${syncedCount === 1 ? '' : 's'} synced successfully`,
      {
        type: 'sync_completed',
        syncedCount,
      }
    );
  }

  async notifySyncFailed(errorCount: number): Promise<void> {
    await this.sendLocalNotification(
      'Sync Failed',
      `${errorCount} item${errorCount === 1 ? '' : 's'} failed to sync. Please check your connection.`,
      {
        type: 'sync_failed',
        errorCount,
      }
    );
  }

  getExpoPushToken(): string | null {
    return this.expoPushToken;
  }
}

export const notificationService = NotificationService.getInstance();
