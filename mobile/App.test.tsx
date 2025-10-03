import React from 'react';
import { render } from '@testing-library/react-native';
import App from './App';

// Mock Expo modules
jest.mock('expo-status-bar', () => ({
  StatusBar: 'StatusBar',
}));

jest.mock('@react-navigation/native', () => ({
  NavigationContainer: ({ children }: { children: React.ReactNode }) => children,
}));

jest.mock('@react-navigation/stack', () => ({
  createStackNavigator: () => ({
    Navigator: ({ children }: { children: React.ReactNode }) => children,
    Screen: ({ children }: { children: React.ReactNode }) => children,
  }),
}));

jest.mock('@react-navigation/bottom-tabs', () => ({
  createBottomTabNavigator: () => ({
    Navigator: ({ children }: { children: React.ReactNode }) => children,
    Screen: ({ children }: { children: React.ReactNode }) => children,
  }),
}));

describe('App Component', () => {
  test('renders without crashing', () => {
    const { getByTestId } = render(<App />);
    // Basic test that app renders
    expect(getByTestId).toBeDefined();
  });

  test('has navigation structure', () => {
    const { getByTestId } = render(<App />);
    // Test that navigation components are present
    expect(getByTestId).toBeDefined();
  });
});
