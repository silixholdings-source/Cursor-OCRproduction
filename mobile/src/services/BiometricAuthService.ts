/**
 * Biometric Authentication Service
 * Provides secure biometric authentication using device biometrics
 */
import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

export interface BiometricAuthResult {
  success: boolean;
  error?: string;
  biometryType?: LocalAuthentication.AuthenticationType;
}

export interface BiometricCapabilities {
  isAvailable: boolean;
  supportedTypes: LocalAuthentication.AuthenticationType[];
  hasHardware: boolean;
  isEnrolled: boolean;
}

class BiometricAuthService {
  private static instance: BiometricAuthService;
  private isBiometricAvailable: boolean = false;
  private supportedTypes: LocalAuthentication.AuthenticationType[] = [];

  private constructor() {
    this.initializeBiometric();
  }

  public static getInstance(): BiometricAuthService {
    if (!BiometricAuthService.instance) {
      BiometricAuthService.instance = new BiometricAuthService();
    }
    return BiometricAuthService.instance;
  }

  private async initializeBiometric(): Promise<void> {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      const supportedTypes = await LocalAuthentication.supportedAuthenticationTypesAsync();
      
      this.isBiometricAvailable = hasHardware && isEnrolled;
      this.supportedTypes = supportedTypes;
    } catch (error) {
      console.error('Failed to initialize biometric authentication:', error);
      this.isBiometricAvailable = false;
    }
  }

  /**
   * Check if biometric authentication is available and enrolled
   */
  public async getBiometricCapabilities(): Promise<BiometricCapabilities> {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      const supportedTypes = await LocalAuthentication.supportedAuthenticationTypesAsync();

      return {
        isAvailable: hasHardware && isEnrolled,
        supportedTypes,
        hasHardware,
        isEnrolled
      };
    } catch (error) {
      console.error('Failed to get biometric capabilities:', error);
      return {
        isAvailable: false,
        supportedTypes: [],
        hasHardware: false,
        isEnrolled: false
      };
    }
  }

  /**
   * Authenticate using biometrics
   */
  public async authenticateWithBiometrics(
    promptMessage: string = 'Authenticate to access your account',
    fallbackLabel: string = 'Use Passcode'
  ): Promise<BiometricAuthResult> {
    try {
      const capabilities = await this.getBiometricCapabilities();
      
      if (!capabilities.isAvailable) {
        return {
          success: false,
          error: 'Biometric authentication is not available or not enrolled'
        };
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage,
        fallbackLabel,
        disableDeviceFallback: false,
        cancelLabel: 'Cancel',
        requireConfirmation: Platform.OS === 'ios'
      });

      if (result.success) {
        // Store authentication timestamp for session management
        await this.storeAuthenticationTimestamp();
        
        return {
          success: true,
          biometryType: capabilities.supportedTypes[0]
        };
      } else {
        return {
          success: false,
          error: result.error || 'Authentication failed'
        };
      }
    } catch (error) {
      console.error('Biometric authentication error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  /**
   * Quick authentication for returning users
   */
  public async quickAuthenticate(): Promise<BiometricAuthResult> {
    return this.authenticateWithBiometrics(
      'Quick sign in',
      'Use Passcode'
    );
  }

  /**
   * Authenticate for sensitive operations
   */
  public async authenticateForSensitiveOperation(
    operation: string
  ): Promise<BiometricAuthResult> {
    return this.authenticateWithBiometrics(
      `Authenticate to ${operation}`,
      'Use Passcode'
    );
  }

  /**
   * Check if biometric authentication is available
   */
  public async isBiometricAvailable(): Promise<boolean> {
    const capabilities = await this.getBiometricCapabilities();
    return capabilities.isAvailable;
  }

  /**
   * Get the primary biometric type available
   */
  public async getPrimaryBiometricType(): Promise<LocalAuthentication.AuthenticationType | null> {
    const capabilities = await this.getBiometricCapabilities();
    return capabilities.supportedTypes.length > 0 ? capabilities.supportedTypes[0] : null;
  }

  /**
   * Store authentication timestamp for session management
   */
  private async storeAuthenticationTimestamp(): Promise<void> {
    try {
      const timestamp = Date.now().toString();
      await SecureStore.setItemAsync('lastBiometricAuth', timestamp);
    } catch (error) {
      console.error('Failed to store authentication timestamp:', error);
    }
  }

  /**
   * Check if last authentication is still valid (within session timeout)
   */
  public async isLastAuthenticationValid(timeoutMinutes: number = 15): Promise<boolean> {
    try {
      const lastAuthTimestamp = await SecureStore.getItemAsync('lastBiometricAuth');
      
      if (!lastAuthTimestamp) {
        return false;
      }

      const lastAuthTime = parseInt(lastAuthTimestamp, 10);
      const currentTime = Date.now();
      const timeoutMs = timeoutMinutes * 60 * 1000;

      return (currentTime - lastAuthTime) < timeoutMs;
    } catch (error) {
      console.error('Failed to check last authentication validity:', error);
      return false;
    }
  }

  /**
   * Clear stored authentication data
   */
  public async clearAuthenticationData(): Promise<void> {
    try {
      await SecureStore.deleteItemAsync('lastBiometricAuth');
    } catch (error) {
      console.error('Failed to clear authentication data:', error);
    }
  }

  /**
   * Get user-friendly biometric type name
   */
  public getBiometricTypeName(type: LocalAuthentication.AuthenticationType): string {
    switch (type) {
      case LocalAuthentication.AuthenticationType.FINGERPRINT:
        return 'Fingerprint';
      case LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION:
        return 'Face ID';
      case LocalAuthentication.AuthenticationType.IRIS:
        return 'Iris';
      default:
        return 'Biometric';
    }
  }

  /**
   * Get biometric authentication icon
   */
  public getBiometricIcon(type: LocalAuthentication.AuthenticationType): string {
    switch (type) {
      case LocalAuthentication.AuthenticationType.FINGERPRINT:
        return 'fingerprint';
      case LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION:
        return 'face-recognition';
      case LocalAuthentication.AuthenticationType.IRIS:
        return 'eye';
      default:
        return 'shield-check';
    }
  }

  /**
   * Check if biometric authentication is recommended for the device
   */
  public async isBiometricRecommended(): Promise<boolean> {
    const capabilities = await this.getBiometricCapabilities();
    return capabilities.isAvailable && capabilities.supportedTypes.length > 0;
  }

  /**
   * Get security level of biometric authentication
   */
  public async getSecurityLevel(): Promise<'high' | 'medium' | 'low' | 'none'> {
    const capabilities = await this.getBiometricCapabilities();
    
    if (!capabilities.isAvailable) {
      return 'none';
    }

    // Face ID and Iris are considered high security
    if (capabilities.supportedTypes.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION) ||
        capabilities.supportedTypes.includes(LocalAuthentication.AuthenticationType.IRIS)) {
      return 'high';
    }

    // Fingerprint is medium security
    if (capabilities.supportedTypes.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)) {
      return 'medium';
    }

    return 'low';
  }
}

export default BiometricAuthService;








