import * as ImageManipulator from 'expo-image-manipulator';
import * as DocumentPicker from 'expo-document-picker';
import { Camera } from 'expo-camera';
import { Invoice, SyncStatus } from '../types/Invoice';

export interface CaptureResult {
  success: boolean;
  imageUri?: string;
  pdfUri?: string;
  error?: string;
}

export interface InvoiceData {
  vendorName: string;
  invoiceNumber: string;
  invoiceDate: string;
  dueDate: string;
  amount: number;
  currency: string;
  lineItems: Array<{
    description: string;
    quantity: number;
    unitPrice: number;
    amount: number;
  }>;
  totalAmount: number;
  taxAmount: number;
  notes?: string;
}

class InvoiceCaptureService {
  private static instance: InvoiceCaptureService;
  private cameraRef: any = null;

  static getInstance(): InvoiceCaptureService {
    if (!InvoiceCaptureService.instance) {
      InvoiceCaptureService.instance = new InvoiceCaptureService();
    }
    return InvoiceCaptureService.instance;
  }

  setCameraRef(ref: any) {
    this.cameraRef = ref;
  }

  async captureFromCamera(): Promise<CaptureResult> {
    try {
      if (!this.cameraRef) {
        throw new Error('Camera ref not set');
      }

      const photo = await this.cameraRef.takePictureAsync({
        quality: 0.8,
        base64: false,
        exif: false,
      });

      // Process and optimize the image
      const processedImage = await ImageManipulator.manipulateAsync(
        photo.uri,
        [
          {
            resize: { width: 1024 },
          },
        ],
        {
          compress: 0.8,
          format: ImageManipulator.SaveFormat.JPEG,
        }
      );

      return {
        success: true,
        imageUri: processedImage.uri,
      };
    } catch (error) {
      console.error('Camera capture failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Camera capture failed',
      };
    }
  }

  async captureFromGallery(): Promise<CaptureResult> {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['image/*', 'application/pdf'],
        copyToCacheDirectory: true,
      });

      if (result.canceled) {
        return {
          success: false,
          error: 'User canceled selection',
        };
      }

      const asset = result.assets[0];
      if (asset.mimeType?.startsWith('image/')) {
        // Process image
        const processedImage = await ImageManipulator.manipulateAsync(
          asset.uri,
          [
            {
              resize: { width: 1024 },
            },
          ],
          {
            compress: 0.8,
            format: ImageManipulator.SaveFormat.JPEG,
          }
        );

        return {
          success: true,
          imageUri: processedImage.uri,
        };
      } else if (asset.mimeType === 'application/pdf') {
        return {
          success: true,
          pdfUri: asset.uri,
        };
      } else {
        return {
          success: false,
          error: 'Unsupported file type',
        };
      }
    } catch (error) {
      console.error('Gallery capture failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Gallery capture failed',
      };
    }
  }

  async processInvoiceImage(imageUri: string): Promise<InvoiceData> {
    try {
      // In a real implementation, this would call the OCR service
      // For now, we'll return mock data
      const mockData: InvoiceData = {
        vendorName: 'Sample Vendor',
        invoiceNumber: `INV-${Date.now()}`,
        invoiceDate: new Date().toISOString().split('T')[0],
        dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        amount: 1000.00,
        currency: 'USD',
        lineItems: [
          {
            description: 'Sample Item',
            quantity: 1,
            unitPrice: 1000.00,
            amount: 1000.00,
          },
        ],
        totalAmount: 1000.00,
        taxAmount: 0.00,
        notes: 'Captured from mobile app',
      };

      return mockData;
    } catch (error) {
      console.error('Image processing failed:', error);
      throw new Error('Failed to process invoice image');
    }
  }

  async validateInvoiceData(data: InvoiceData): Promise<{ isValid: boolean; errors: string[] }> {
    const errors: string[] = [];

    if (!data.vendorName) {
      errors.push('Vendor name is required');
    }

    if (!data.invoiceNumber) {
      errors.push('Invoice number is required');
    }

    if (!data.invoiceDate) {
      errors.push('Invoice date is required');
    }

    if (!data.amount || data.amount <= 0) {
      errors.push('Valid amount is required');
    }

    if (data.lineItems.length === 0) {
      errors.push('At least one line item is required');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  async saveInvoiceDraft(data: InvoiceData, imageUri?: string): Promise<Invoice> {
    try {
      const invoice: Invoice = {
        id: `draft_${Date.now()}`,
        vendorName: data.vendorName,
        invoiceNumber: data.invoiceNumber,
        invoiceDate: data.invoiceDate,
        dueDate: data.dueDate,
        amount: data.amount,
        currency: data.currency,
        lineItems: data.lineItems,
        totalAmount: data.totalAmount,
        taxAmount: data.taxAmount,
        notes: data.notes,
        status: 'draft',
        syncStatus: SyncStatus.PENDING,
        isOffline: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        imageUri,
      };

      // Save to offline storage
      const { offlineSyncService } = await import('./OfflineSyncService');
      await offlineSyncService.saveInvoiceOffline(invoice);

      return invoice;
    } catch (error) {
      console.error('Failed to save invoice draft:', error);
      throw error;
    }
  }
}

export const invoiceCaptureService = InvoiceCaptureService.getInstance();








