import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { View, Text, StyleSheet, Alert } from 'react-native';
import * as Notifications from 'expo-notifications';
import * as Network from 'expo-network';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import screens
import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import InvoiceListScreen from './src/screens/InvoiceListScreen';
import InvoiceDetailScreen from './src/screens/InvoiceDetailScreen';
import CameraScreen from './src/screens/CameraScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import OfflineSyncScreen from './src/screens/OfflineSyncScreen';
import { InvoiceCaptureScreen } from './src/screens/InvoiceCaptureScreen';
import { OfflineInvoicesScreen } from './src/screens/OfflineInvoicesScreen';

// Import components
import LoadingSpinner from './src/components/LoadingSpinner';
import OfflineBanner from './src/components/OfflineBanner';

// Import services
import { AuthService } from './src/services/AuthService';
import { OfflineSyncService } from './src/services/OfflineSyncService';
import { NotificationService } from './src/services/NotificationService';
import { offlineSyncService } from './src/services/OfflineSyncService';
import { pushNotificationService } from './src/services/PushNotificationService';

// Import types
import { User } from './src/types/User';
import { Invoice } from './src/types/Invoice';

// Configure notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Tab Navigator Component
function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarStyle: {
          backgroundColor: '#1f2937',
          borderTopColor: '#374151',
        },
        tabBarActiveTintColor: '#3b82f6',
        tabBarInactiveTintColor: '#9ca3af',
        headerStyle: {
          backgroundColor: '#1f2937',
        },
        headerTintColor: '#ffffff',
      }}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ color, size }) => (
            <Text style={{ color, fontSize: size }}>📊</Text>
          ),
        }}
      />
      <Tab.Screen 
        name="Invoices" 
        component={InvoiceListScreen}
        options={{
          title: 'Invoices',
          tabBarIcon: ({ color, size }) => (
            <Text style={{ color, fontSize: size }}>📄</Text>
          ),
        }}
      />
      <Tab.Screen 
        name="Camera" 
        component={InvoiceCaptureScreen}
        options={{
          title: 'Scan',
          tabBarIcon: ({ color, size }) => (
            <Text style={{ color, fontSize: size }}>📷</Text>
          ),
        }}
      />
      <Tab.Screen 
        name="Offline" 
        component={OfflineInvoicesScreen}
        options={{
          title: 'Offline',
          tabBarIcon: ({ color, size }) => (
            <Text style={{ color, fontSize: size }}>📱</Text>
          ),
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <Text style={{ color, fontSize: size }}>👤</Text>
          ),
        }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isOffline, setIsOffline] = useState(false);
  const [pendingSyncCount, setPendingSyncCount] = useState(0);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Check network connectivity
      const networkState = await Network.getNetworkStateAsync();
      setIsOffline(!networkState.isConnected);

      // Set up network listener
      const unsubscribe = Network.addNetworkStateListener((networkState) => {
        setIsOffline(!networkState.isConnected);
      });

      // Initialize notification service
      await NotificationService.initialize();
      await pushNotificationService.initialize();

      // Check authentication status
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        try {
          const userData = await AuthService.getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error) {
          console.log('Token invalid, logging out');
          await AuthService.logout();
        }
      }

      // Initialize offline sync service
      await OfflineSyncService.initialize();
      await offlineSyncService.initialize();
      const pendingCount = await OfflineSyncService.getPendingSyncCount();
      setPendingSyncCount(pendingCount);

      // Set up notification listeners
      const notificationListener = Notifications.addNotificationReceivedListener(
        (notification) => {
          console.log('Notification received:', notification);
        }
      );

      const responseListener = Notifications.addNotificationResponseReceivedListener(
        (response) => {
          console.log('Notification response:', response);
          // Handle notification tap
          handleNotificationResponse(response);
        }
      );

      setIsLoading(false);

      // Cleanup function
      return () => {
        unsubscribe();
        notificationListener.remove();
        responseListener.remove();
      };
    } catch (error) {
      console.error('App initialization error:', error);
      setIsLoading(false);
    }
  };

  const handleNotificationResponse = (response: Notifications.NotificationResponse) => {
    const { data } = response.notification.request.content;
    
    if (data?.type === 'invoice_approval') {
      // Navigate to invoice detail screen
      console.log('Navigate to invoice:', data.invoiceId);
    } else if (data?.type === 'trial_reminder') {
      // Show trial reminder
      Alert.alert(
        'Trial Reminder',
        'Your trial will expire soon. Consider upgrading to continue using the app.',
        [{ text: 'OK' }]
      );
    }
  };

  const handleLogin = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const userData = await AuthService.login(email, password);
      setUser(userData);
      setIsAuthenticated(true);
      
      // Set up push notifications
      await NotificationService.registerForPushNotifications();
      await pushNotificationService.registerForPushNotifications();
    } catch (error) {
      console.error('Login error:', error);
      Alert.alert('Login Failed', 'Invalid credentials. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await AuthService.logout();
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <LoadingSpinner size="large" />
        <Text style={styles.loadingText}>Loading AI ERP...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {isOffline && <OfflineBanner pendingCount={pendingSyncCount} />}
      
      <NavigationContainer>
        <Stack.Navigator
          screenOptions={{
            headerStyle: {
              backgroundColor: '#1f2937',
            },
            headerTintColor: '#ffffff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        >
          {!isAuthenticated ? (
            <Stack.Screen 
              name="Login" 
              options={{ headerShown: false }}
            >
              {(props) => <LoginScreen {...props} onLogin={handleLogin} />}
            </Stack.Screen>
          ) : (
            <>
              <Stack.Screen 
                name="Main" 
                component={TabNavigator}
                options={{ headerShown: false }}
              />
              <Stack.Screen 
                name="InvoiceDetail" 
                component={InvoiceDetailScreen}
                options={{ title: 'Invoice Details' }}
              />
              <Stack.Screen 
                name="OfflineSync" 
                component={OfflineSyncScreen}
                options={{ title: 'Offline Sync' }}
              />
            </>
          )}
        </Stack.Navigator>
      </NavigationContainer>
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
  loadingText: {
    color: '#ffffff',
    fontSize: 18,
    marginTop: 16,
    fontWeight: '500',
  },
});
