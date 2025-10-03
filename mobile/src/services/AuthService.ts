import AsyncStorage from '@react-native-async-storage/async-storage';
import { User, LoginCredentials, AuthResponse } from '../types/User';

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1' 
  : 'https://api.ai-erp-saas.com/api/v1';

class AuthService {
  private static instance: AuthService;
  private authToken: string | null = null;

  static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  async login(credentials: LoginCredentials): Promise<User> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const authData: AuthResponse = await response.json();
      
      // Store tokens
      await AsyncStorage.setItem('auth_token', authData.token);
      await AsyncStorage.setItem('refresh_token', authData.refreshToken);
      await AsyncStorage.setItem('user_data', JSON.stringify(authData.user));
      
      this.authToken = authData.token;
      
      return authData.user;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      // Call logout endpoint if token exists
      if (this.authToken) {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.authToken}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.error('Logout API error:', error);
    } finally {
      // Clear local storage regardless of API call result
      await AsyncStorage.multiRemove(['auth_token', 'refresh_token', 'user_data']);
      this.authToken = null;
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, try to refresh
          await this.refreshToken();
          return this.getCurrentUser();
        }
        throw new Error('Failed to get current user');
      }

      const user: User = await response.json();
      await AsyncStorage.setItem('user_data', JSON.stringify(user));
      
      return user;
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  }

  async refreshToken(): Promise<void> {
    try {
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token found');
      }

      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const authData: AuthResponse = await response.json();
      
      await AsyncStorage.setItem('auth_token', authData.token);
      await AsyncStorage.setItem('refresh_token', authData.refreshToken);
      
      this.authToken = authData.token;
    } catch (error) {
      console.error('Token refresh error:', error);
      // If refresh fails, logout user
      await this.logout();
      throw error;
    }
  }

  async getStoredUser(): Promise<User | null> {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Get stored user error:', error);
      return null;
    }
  }

  async isAuthenticated(): Promise<boolean> {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      return !!token;
    } catch (error) {
      console.error('Check authentication error:', error);
      return false;
    }
  }

  getAuthHeaders(): Record<string, string> {
    return {
      'Authorization': `Bearer ${this.authToken}`,
      'Content-Type': 'application/json',
    };
  }
}

export const authService = AuthService.getInstance();
