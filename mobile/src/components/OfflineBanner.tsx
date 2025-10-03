import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

interface Props {
  pendingCount: number;
  onSyncPress?: () => void;
}

export default function OfflineBanner({ pendingCount, onSyncPress }: Props) {
  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.icon}>📡</Text>
        <View style={styles.textContainer}>
          <Text style={styles.title}>You're offline</Text>
          <Text style={styles.subtitle}>
            {pendingCount} item{pendingCount === 1 ? '' : 's'} pending sync
          </Text>
        </View>
        {onSyncPress && (
          <TouchableOpacity style={styles.syncButton} onPress={onSyncPress}>
            <Text style={styles.syncButtonText}>Sync</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#f59e0b',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#d97706',
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    fontSize: 20,
    marginRight: 12,
  },
  textContainer: {
    flex: 1,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 2,
  },
  subtitle: {
    fontSize: 14,
    color: '#fef3c7',
  },
  syncButton: {
    backgroundColor: '#ffffff',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  syncButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#f59e0b',
  },
});
