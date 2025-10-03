import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ScrollView,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { Camera } from 'expo-camera';
import { Ionicons } from '@expo/vector-icons';
import { invoiceCaptureService, InvoiceData } from '../services/InvoiceCaptureService';
import { offlineSyncService } from '../services/OfflineSyncService';
import { pushNotificationService } from '../services/PushNotificationService';

interface InvoiceCaptureScreenProps {
  navigation: any;
}

export const InvoiceCaptureScreen: React.FC<InvoiceCaptureScreenProps> = ({ navigation }) => {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [cameraType, setCameraType] = useState(Camera.Constants.Type.back);
  const [isCapturing, setIsCapturing] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [invoiceData, setInvoiceData] = useState<InvoiceData | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [pendingSyncCount, setPendingSyncCount] = useState(0);
  
  const cameraRef = useRef<Camera>(null);

  useEffect(() => {
    getCameraPermission();
    checkPendingSync();
    invoiceCaptureService.setCameraRef(cameraRef.current);
  }, []);

  const getCameraPermission = async () => {
    const { status } = await Camera.requestCameraPermissionsAsync();
    setHasPermission(status === 'granted');
  };

  const checkPendingSync = async () => {
    try {
      const count = await offlineSyncService.getPendingSyncCount();
      setPendingSyncCount(count);
    } catch (error) {
      console.error('Failed to check pending sync:', error);
    }
  };

  const handleCaptureFromCamera = async () => {
    setIsCapturing(true);
    try {
      const result = await invoiceCaptureService.captureFromCamera();
      if (result.success && result.imageUri) {
        setCapturedImage(result.imageUri);
        await processImage(result.imageUri);
      } else {
        Alert.alert('Capture Failed', result.error || 'Failed to capture image');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to capture image');
    } finally {
      setIsCapturing(false);
    }
  };

  const handleCaptureFromGallery = async () => {
    setIsCapturing(true);
    try {
      const result = await invoiceCaptureService.captureFromGallery();
      if (result.success) {
        if (result.imageUri) {
          setCapturedImage(result.imageUri);
          await processImage(result.imageUri);
        } else if (result.pdfUri) {
          // Handle PDF
          Alert.alert('PDF Detected', 'PDF processing will be implemented in the next version');
        }
      } else {
        Alert.alert('Selection Failed', result.error || 'Failed to select file');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to select file');
    } finally {
      setIsCapturing(false);
    }
  };

  const processImage = async (imageUri: string) => {
    setIsProcessing(true);
    try {
      const data = await invoiceCaptureService.processInvoiceImage(imageUri);
      setInvoiceData(data);
    } catch (error) {
      Alert.alert('Processing Failed', 'Failed to process invoice image');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSaveInvoice = async () => {
    if (!invoiceData) return;

    // Validate invoice data
    const validation = await invoiceCaptureService.validateInvoiceData(invoiceData);
    if (!validation.isValid) {
      Alert.alert('Validation Failed', validation.errors.join('\n'));
      return;
    }

    setIsSaving(true);
    try {
      const invoice = await invoiceCaptureService.saveInvoiceDraft(invoiceData, capturedImage || undefined);
      
      // Send local notification
      await pushNotificationService.sendLocalNotification(
        'Invoice Saved',
        `Invoice ${invoice.invoiceNumber} has been saved offline`,
        { type: 'invoice_saved', invoiceId: invoice.id }
      );

      // Check pending sync count
      await checkPendingSync();

      Alert.alert(
        'Success',
        'Invoice saved offline. It will be synced when you have internet connection.',
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error) {
      Alert.alert('Save Failed', 'Failed to save invoice');
    } finally {
      setIsSaving(false);
    }
  };

  const handleSyncNow = async () => {
    try {
      await offlineSyncService.syncOfflineData();
      await checkPendingSync();
      Alert.alert('Sync Complete', 'Offline data has been synced');
    } catch (error) {
      Alert.alert('Sync Failed', 'Failed to sync offline data');
    }
  };

  if (hasPermission === null) {
    return (
      <View style={styles.container}>
        <Text>Requesting camera permission...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>No access to camera</Text>
        <TouchableOpacity style={styles.button} onPress={getCameraPermission}>
          <Text style={styles.buttonText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Capture Invoice</Text>
        {pendingSyncCount > 0 && (
          <TouchableOpacity style={styles.syncButton} onPress={handleSyncNow}>
            <Ionicons name="sync" size={20} color="#fff" />
            <Text style={styles.syncText}>{pendingSyncCount}</Text>
          </TouchableOpacity>
        )}
      </View>

      {!capturedImage ? (
        <View style={styles.cameraContainer}>
          <Camera
            ref={cameraRef}
            style={styles.camera}
            type={cameraType}
            ratio="16:9"
          >
            <View style={styles.cameraOverlay}>
              <View style={styles.captureButtons}>
                <TouchableOpacity
                  style={styles.captureButton}
                  onPress={handleCaptureFromCamera}
                  disabled={isCapturing}
                >
                  <Ionicons name="camera" size={30} color="#fff" />
                </TouchableOpacity>
                
                <TouchableOpacity
                  style={styles.galleryButton}
                  onPress={handleCaptureFromGallery}
                  disabled={isCapturing}
                >
                  <Ionicons name="images" size={30} color="#fff" />
                </TouchableOpacity>
              </View>
            </View>
          </Camera>
        </View>
      ) : (
        <View style={styles.previewContainer}>
          <Text style={styles.previewTitle}>Captured Image</Text>
          <TouchableOpacity
            style={styles.retakeButton}
            onPress={() => {
              setCapturedImage(null);
              setInvoiceData(null);
            }}
          >
            <Text style={styles.retakeText}>Retake</Text>
          </TouchableOpacity>
        </View>
      )}

      {isProcessing && (
        <View style={styles.processingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.processingText}>Processing invoice...</Text>
        </View>
      )}

      {invoiceData && (
        <View style={styles.invoiceForm}>
          <Text style={styles.formTitle}>Invoice Details</Text>
          
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Vendor Name</Text>
            <TextInput
              style={styles.input}
              value={invoiceData.vendorName}
              onChangeText={(text) => setInvoiceData({ ...invoiceData, vendorName: text })}
              placeholder="Enter vendor name"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Invoice Number</Text>
            <TextInput
              style={styles.input}
              value={invoiceData.invoiceNumber}
              onChangeText={(text) => setInvoiceData({ ...invoiceData, invoiceNumber: text })}
              placeholder="Enter invoice number"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Amount</Text>
            <TextInput
              style={styles.input}
              value={invoiceData.amount.toString()}
              onChangeText={(text) => setInvoiceData({ ...invoiceData, amount: parseFloat(text) || 0 })}
              placeholder="Enter amount"
              keyboardType="numeric"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Notes</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              value={invoiceData.notes || ''}
              onChangeText={(text) => setInvoiceData({ ...invoiceData, notes: text })}
              placeholder="Enter notes (optional)"
              multiline
              numberOfLines={3}
            />
          </View>

          <TouchableOpacity
            style={[styles.saveButton, isSaving && styles.disabledButton]}
            onPress={handleSaveInvoice}
            disabled={isSaving}
          >
            {isSaving ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.saveButtonText}>Save Invoice</Text>
            )}
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  syncButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#007AFF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  syncText: {
    color: '#fff',
    marginLeft: 4,
    fontWeight: 'bold',
  },
  cameraContainer: {
    height: 300,
    margin: 20,
    borderRadius: 10,
    overflow: 'hidden',
  },
  camera: {
    flex: 1,
  },
  cameraOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.3)',
  },
  captureButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    paddingBottom: 30,
  },
  captureButton: {
    backgroundColor: '#007AFF',
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  galleryButton: {
    backgroundColor: '#34C759',
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  previewContainer: {
    margin: 20,
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 10,
    alignItems: 'center',
  },
  previewTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  retakeButton: {
    backgroundColor: '#FF3B30',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
  },
  retakeText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  processingContainer: {
    alignItems: 'center',
    padding: 40,
  },
  processingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  invoiceForm: {
    margin: 20,
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 10,
  },
  formTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  inputGroup: {
    marginBottom: 15,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 5,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  saveButton: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 20,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  message: {
    textAlign: 'center',
    fontSize: 16,
    color: '#666',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    margin: 20,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});








