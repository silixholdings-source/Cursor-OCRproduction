import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet } from 'react-native';

interface Props {
  size?: 'small' | 'large';
  color?: string;
  text?: string;
}

export default function LoadingSpinner({ 
  size = 'large', 
  color = '#3b82f6', 
  text 
}: Props) {
  return (
    <View style={styles.container}>
      <ActivityIndicator size={size} color={color} />
      {text && <Text style={styles.text}>{text}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    marginTop: 12,
    fontSize: 16,
    color: '#ffffff',
    textAlign: 'center',
  },
});
