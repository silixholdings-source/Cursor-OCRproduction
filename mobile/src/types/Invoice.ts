export interface Invoice {
  id: string;
  invoiceNumber: string;
  supplierName: string;
  supplierEmail?: string;
  supplierPhone?: string;
  supplierAddress?: string;
  supplierTaxId?: string;
  invoiceDate: string;
  dueDate?: string;
  totalAmount: number;
  currency: string;
  taxAmount: number;
  taxRate: number;
  subtotal: number;
  totalWithTax: number;
  status: InvoiceStatus;
  invoiceType: InvoiceType;
  companyId: string;
  createdBy: string;
  approvedBy?: string;
  approvedAt?: string;
  rejectedBy?: string;
  rejectedAt?: string;
  rejectionReason?: string;
  postedToErpAt?: string;
  erpReference?: string;
  createdAt: string;
  updatedAt: string;
  // OCR specific fields
  ocrData?: OCRData;
  ocrConfidence?: number;
  ocrProcessedAt?: string;
  // Offline sync fields
  isOffline?: boolean;
  syncStatus?: SyncStatus;
  lastSyncAt?: string;
}

export enum InvoiceStatus {
  DRAFT = 'draft',
  PENDING_APPROVAL = 'pending_approval',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  POSTED_TO_ERP = 'posted_to_erp',
  ERROR = 'error',
  CANCELLED = 'cancelled',
}

export enum InvoiceType {
  INVOICE = 'invoice',
  CREDIT_MEMO = 'credit_memo',
  DEBIT_MEMO = 'debit_memo',
  RECURRING = 'recurring',
}

export enum SyncStatus {
  PENDING = 'pending',
  SYNCING = 'syncing',
  SYNCED = 'synced',
  FAILED = 'failed',
}

export interface OCRData {
  extractedText: string;
  lineItems: LineItem[];
  totals: {
    subtotal: number;
    tax: number;
    total: number;
  };
  confidence: number;
  processingTime: number;
}

export interface LineItem {
  description: string;
  quantity: number;
  unitPrice: number;
  total: number;
  glCode?: string;
  costCenter?: string;
}

export interface InvoiceListResponse {
  invoices: Invoice[];
  total: number;
  page: number;
  perPage: number;
  totalPages: number;
}

export interface InvoiceCreateRequest {
  invoiceNumber: string;
  supplierName: string;
  supplierEmail?: string;
  supplierPhone?: string;
  supplierAddress?: string;
  supplierTaxId?: string;
  invoiceDate: string;
  dueDate?: string;
  totalAmount: number;
  currency?: string;
  taxAmount?: number;
  taxRate?: number;
  subtotal: number;
  totalWithTax: number;
  invoiceType?: InvoiceType;
  ocrData?: OCRData;
}

export interface InvoiceUpdateRequest {
  supplierName?: string;
  supplierEmail?: string;
  supplierPhone?: string;
  supplierAddress?: string;
  supplierTaxId?: string;
  invoiceDate?: string;
  dueDate?: string;
  totalAmount?: number;
  currency?: string;
  taxAmount?: number;
  taxRate?: number;
  subtotal?: number;
  totalWithTax?: number;
  status?: InvoiceStatus;
  invoiceType?: InvoiceType;
}
