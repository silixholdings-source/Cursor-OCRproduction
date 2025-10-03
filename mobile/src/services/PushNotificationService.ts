import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import { authService } from './AuthService';

interface NotificationData {
  type: 'invoice_approved' | 'invoice_rejected' | 'invoice_pending' | 'sync_completed' | 'sync_failed';
  invoiceId?: string;
  message: string;
  data?: any;
}

class PushNotificationService {
  private static instance: PushNotificationService;
  private expoPushToken: string | null = null;
  private notificationListener: any = null;
  private responseListener: any = null;

  static getInstance(): PushNotificationService {
    if (!PushNotificationService.instance) {
      PushNotificationService.instance = new PushNotificationService();
    }
    return PushNotificationService.instance;
  }

  async initialize(): Promise<void> {
    try {
      // Request permissions
      const { status } = await Notifications.requestPermissionsAsync();
      if (status !== 'granted') {
        throw new Error('Notification permission not granted');
      }

      // Configure notification behavior
      Notifications.setNotificationHandler({
        handleNotification: async () => ({
          shouldShowAlert: true,
          shouldPlaySound: true,
          shouldSetBadge: false,
        }),
      });

      // Get push token
      if (Device.isDevice) {
        this.expoPushToken = (await Notifications.getExpoPushTokenAsync()).data;
        console.log('Expo push token:', this.expoPushToken);
      } else {
        console.log('Must use physical device for Push Notifications');
      }

      // Set up notification listeners
      this.setupNotificationListeners();

      console.log('PushNotificationService initialized');
    } catch (error) {
      console.error('Failed to initialize PushNotificationService:', error);
      throw error;
    }
  }

  private setupNotificationListeners(): void {
    // Handle notifications received while app is foregrounded
    this.notificationListener = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log('Notification received:', notification);
        this.handleNotificationReceived(notification);
      }
    );

    // Handle notification taps
    this.responseListener = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        console.log('Notification tapped:', response);
        this.handleNotificationTapped(response);
      }
    );
  }

  private handleNotificationReceived(notification: Notifications.Notification): void {
    const data = notification.request.content.data as NotificationData;
    
    switch (data.type) {
      case 'invoice_approved':
        this.handleInvoiceApproved(data);
        break;
      case 'invoice_rejected':
        this.handleInvoiceRejected(data);
        break;
      case 'invoice_pending':
        this.handleInvoicePending(data);
        break;
      case 'sync_completed':
        this.handleSyncCompleted(data);
        break;
      case 'sync_failed':
        this.handleSyncFailed(data);
        break;
    }
  }

  private handleNotificationTapped(response: Notifications.NotificationResponse): void {
    const data = response.notification.request.content.data as NotificationData;
    
    // Navigate to appropriate screen based on notification type
    switch (data.type) {
      case 'invoice_approved':
      case 'invoice_rejected':
      case 'invoice_pending':
        if (data.invoiceId) {
          // Navigate to invoice details
          console.log('Navigate to invoice:', data.invoiceId);
        }
        break;
      case 'sync_completed':
      case 'sync_failed':
        // Navigate to sync status or home screen
        console.log('Navigate to sync status');
        break;
    }
  }

  private handleInvoiceApproved(data: NotificationData): void {
    // Update local invoice status
    console.log('Invoice approved:', data.invoiceId);
  }

  private handleInvoiceRejected(data: NotificationData): void {
    // Update local invoice status
    console.log('Invoice rejected:', data.invoiceId);
  }

  private handleInvoicePending(data: NotificationData): void {
    // Show pending notification
    console.log('Invoice pending approval:', data.invoiceId);
  }

  private handleSyncCompleted(data: NotificationData): void {
    // Update sync status
    console.log('Sync completed successfully');
  }

  private handleSyncFailed(data: NotificationData): void {
    // Show sync error
    console.log('Sync failed:', data.message);
  }

  async sendLocalNotification(title: string, body: string, data?: any): Promise<void> {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
        },
        trigger: null, // Show immediately
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

  async getExpoPushToken(): Promise<string | null> {
    return this.expoPushToken;
  }

  async registerForPushNotifications(): Promise<string | null> {
    try {
      if (!Device.isDevice) {
        console.log('Must use physical device for Push Notifications');
        return null;
      }

      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.log('Failed to get push token for push notification!');
        return null;
      }

      const token = (await Notifications.getExpoPushTokenAsync()).data;
      console.log('Push token:', token);

      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('default', {
          name: 'default',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#FF231F7C',
        });
      }

      return token;
    } catch (error) {
      console.error('Failed to register for push notifications:', error);
      return null;
    }
  }

  cleanup(): void {
    if (this.notificationListener) {
      Notifications.removeNotificationSubscription(this.notificationListener);
    }
    if (this.responseListener) {
      Notifications.removeNotificationSubscription(this.responseListener);
    }
  }
}

export const pushNotificationService = PushNotificationService.getInstance();








