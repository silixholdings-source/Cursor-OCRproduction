import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function InvoiceDetailScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Invoice Detail Screen</Text>
      <Text style={styles.subtitle}>Coming soon...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#111827',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#9ca3af',
  },
});
