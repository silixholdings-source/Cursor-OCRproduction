"""
Golden Datasets for AI ERP SaaS Testing
World-class test datasets for OCR, invoice processing, and ML model validation
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import uuid

@dataclass
class GoldenInvoiceData:
    """Golden dataset entry for invoice testing"""
    id: str
    file_path: str
    expected_data: Dict[str, Any]
    confidence_thresholds: Dict[str, float]
    test_category: str
    description: str
    complexity_level: str  # simple, medium, complex
    source_country: str
    currency: str
    language: str

class GoldenDatasetManager:
    """Manager for golden datasets used in testing"""
    
    def __init__(self):
        self.invoice_datasets = self._load_invoice_datasets()
        self.ocr_test_cases = self._load_ocr_test_cases()
        self.erp_test_cases = self._load_erp_test_cases()
        self.ml_test_cases = self._load_ml_test_cases()
    
    def _load_invoice_datasets(self) -> List[GoldenInvoiceData]:
        """Load comprehensive invoice test datasets"""
        datasets = []
        
        # Simple invoices
        datasets.extend([
            GoldenInvoiceData(
                id="simple_invoice_001",
                file_path="test_invoices/simple_invoice_001.pdf",
                expected_data={
                    "supplier_name": "Tech Solutions Inc.",
                    "invoice_number": "TS-2024-001",
                    "invoice_date": "2024-01-15",
                    "due_date": "2024-02-14",
                    "total_amount": 2500.00,
                    "currency": "USD",
                    "tax_amount": 200.00,
                    "subtotal": 2300.00,
                    "line_items": [
                        {
                            "description": "Software License - Annual",
                            "quantity": 1,
                            "unit_price": 2000.00,
                            "total": 2000.00
                        },
                        {
                            "description": "Implementation Services",
                            "quantity": 10,
                            "unit_price": 30.00,
                            "total": 300.00
                        }
                    ]
                },
                confidence_thresholds={
                    "supplier_name": 0.98,
                    "invoice_number": 0.99,
                    "total_amount": 0.99,
                    "line_items": 0.95
                },
                test_category="simple",
                description="Standard business invoice with clear layout",
                complexity_level="simple",
                source_country="US",
                currency="USD",
                language="en"
            ),
            
            GoldenInvoiceData(
                id="simple_invoice_002",
                file_path="test_invoices/simple_invoice_002.pdf",
                expected_data={
                    "supplier_name": "Global Services Ltd.",
                    "invoice_number": "GS-2024-002",
                    "invoice_date": "2024-01-20",
                    "due_date": "2024-02-19",
                    "total_amount": 8500.00,
                    "currency": "USD",
                    "tax_amount": 680.00,
                    "subtotal": 7820.00,
                    "line_items": [
                        {
                            "description": "Consulting Services",
                            "quantity": 40,
                            "unit_price": 150.00,
                            "total": 6000.00
                        },
                        {
                            "description": "Project Management",
                            "quantity": 20,
                            "unit_price": 91.00,
                            "total": 1820.00
                        }
                    ]
                },
                confidence_thresholds={
                    "supplier_name": 0.98,
                    "invoice_number": 0.99,
                    "total_amount": 0.99,
                    "line_items": 0.95
                },
                test_category="simple",
                description="Professional services invoice",
                complexity_level="simple",
                source_country="US",
                currency="USD",
                language="en"
            )
        ])
        
        # Medium complexity invoices
        datasets.extend([
            GoldenInvoiceData(
                id="medium_invoice_001",
                file_path="test_invoices/medium_invoice_001.pdf",
                expected_data={
                    "supplier_name": "Manufacturing Corp.",
                    "invoice_number": "MC-2024-003",
                    "invoice_date": "2024-01-25",
                    "due_date": "2024-03-25",
                    "total_amount": 15650.00,
                    "currency": "USD",
                    "tax_amount": 1252.00,
                    "subtotal": 14398.00,
                    "line_items": [
                        {
                            "description": "Raw Materials - Steel Sheets",
                            "quantity": 500,
                            "unit_price": 15.50,
                            "total": 7750.00
                        },
                        {
                            "description": "Machining Services",
                            "quantity": 200,
                            "unit_price": 25.00,
                            "total": 5000.00
                        },
                        {
                            "description": "Quality Inspection",
                            "quantity": 50,
                            "unit_price": 32.96,
                            "total": 1648.00
                        }
                    ],
                    "shipping_address": {
                        "company": "ABC Manufacturing",
                        "address": "123 Industrial Blvd",
                        "city": "Detroit",
                        "state": "MI",
                        "zip": "48201"
                    }
                },
                confidence_thresholds={
                    "supplier_name": 0.96,
                    "invoice_number": 0.98,
                    "total_amount": 0.98,
                    "line_items": 0.92,
                    "shipping_address": 0.90
                },
                test_category="medium",
                description="Manufacturing invoice with multiple line items and shipping info",
                complexity_level="medium",
                source_country="US",
                currency="USD",
                language="en"
            ),
            
            GoldenInvoiceData(
                id="medium_invoice_002",
                file_path="test_invoices/medium_invoice_002.pdf",
                expected_data={
                    "supplier_name": "European Solutions AG",
                    "invoice_number": "ES-2024-004",
                    "invoice_date": "2024-02-01",
                    "due_date": "2024-03-02",
                    "total_amount": 8750.00,
                    "currency": "EUR",
                    "tax_amount": 1750.00,
                    "subtotal": 7000.00,
                    "line_items": [
                        {
                            "description": "Software Development Services",
                            "quantity": 100,
                            "unit_price": 70.00,
                            "total": 7000.00
                        }
                    ],
                    "vat_number": "DE123456789",
                    "payment_terms": "Net 30"
                },
                confidence_thresholds={
                    "supplier_name": 0.95,
                    "invoice_number": 0.97,
                    "total_amount": 0.98,
                    "line_items": 0.94,
                    "vat_number": 0.92
                },
                test_category="medium",
                description="European invoice with VAT information",
                complexity_level="medium",
                source_country="DE",
                currency="EUR",
                language="de"
            )
        ])
        
        # Complex invoices
        datasets.extend([
            GoldenInvoiceData(
                id="complex_invoice_001",
                file_path="test_invoices/complex_invoice_001.pdf",
                expected_data={
                    "supplier_name": "Multi-National Corporation",
                    "invoice_number": "MNC-2024-005",
                    "invoice_date": "2024-02-05",
                    "due_date": "2024-03-07",
                    "total_amount": 45620.50,
                    "currency": "USD",
                    "tax_amount": 3649.64,
                    "subtotal": 41970.86,
                    "line_items": [
                        {
                            "description": "Enterprise Software License - 3 Year",
                            "quantity": 1,
                            "unit_price": 25000.00,
                            "total": 25000.00
                        },
                        {
                            "description": "Implementation & Training",
                            "quantity": 1,
                            "unit_price": 8500.00,
                            "total": 8500.00
                        },
                        {
                            "description": "Data Migration Services",
                            "quantity": 1,
                            "unit_price": 4200.00,
                            "total": 4200.00
                        },
                        {
                            "description": "Ongoing Support - Year 1",
                            "quantity": 1,
                            "unit_price": 3270.86,
                            "total": 3270.86
                        },
                        {
                            "description": "Custom Integration Development",
                            "quantity": 1,
                            "unit_price": 1000.00,
                            "total": 1000.00
                        }
                    ],
                    "billing_address": {
                        "company": "Enterprise Client Inc.",
                        "address": "456 Corporate Plaza",
                        "city": "New York",
                        "state": "NY",
                        "zip": "10001"
                    },
                    "shipping_address": {
                        "company": "Enterprise Client Inc.",
                        "address": "789 Tech Center",
                        "city": "San Francisco",
                        "state": "CA",
                        "zip": "94105"
                    },
                    "payment_terms": "Net 30",
                    "po_number": "PO-2024-001",
                    "contract_number": "CNT-2024-005"
                },
                confidence_thresholds={
                    "supplier_name": 0.94,
                    "invoice_number": 0.97,
                    "total_amount": 0.97,
                    "line_items": 0.90,
                    "billing_address": 0.88,
                    "shipping_address": 0.88,
                    "po_number": 0.92,
                    "contract_number": 0.90
                },
                test_category="complex",
                description="Complex enterprise invoice with multiple addresses and references",
                complexity_level="complex",
                source_country="US",
                currency="USD",
                language="en"
            ),
            
            GoldenInvoiceData(
                id="complex_invoice_002",
                file_path="test_invoices/complex_invoice_002.pdf",
                expected_data={
                    "supplier_name": "Asia-Pacific Trading Co.",
                    "invoice_number": "APT-2024-006",
                    "invoice_date": "2024-02-10",
                    "due_date": "2024-04-10",
                    "total_amount": 23450.00,
                    "currency": "USD",
                    "tax_amount": 0.00,
                    "subtotal": 23450.00,
                    "line_items": [
                        {
                            "description": "Electronic Components - Resistors",
                            "quantity": 10000,
                            "unit_price": 0.50,
                            "total": 5000.00
                        },
                        {
                            "description": "Electronic Components - Capacitors",
                            "quantity": 5000,
                            "unit_price": 0.75,
                            "total": 3750.00
                        },
                        {
                            "description": "Electronic Components - ICs",
                            "quantity": 1000,
                            "unit_price": 5.00,
                            "total": 5000.00
                        },
                        {
                            "description": "Assembly Services",
                            "quantity": 1000,
                            "unit_price": 2.50,
                            "total": 2500.00
                        },
                        {
                            "description": "Testing & Quality Assurance",
                            "quantity": 1000,
                            "unit_price": 3.20,
                            "total": 3200.00
                        },
                        {
                            "description": "Packaging & Shipping",
                            "quantity": 1,
                            "unit_price": 1000.00,
                            "total": 1000.00
                        }
                    ],
                    "billing_address": {
                        "company": "Tech Manufacturing Ltd.",
                        "address": "88 Technology Street",
                        "city": "Singapore",
                        "state": "",
                        "zip": "138648"
                    },
                    "shipping_address": {
                        "company": "Global Electronics Inc.",
                        "address": "123 Innovation Drive",
                        "city": "Austin",
                        "state": "TX",
                        "zip": "78701"
                    },
                    "incoterms": "FOB Singapore",
                    "hs_code": "8541.40.20",
                    "country_of_origin": "Singapore"
                },
                confidence_thresholds={
                    "supplier_name": 0.93,
                    "invoice_number": 0.96,
                    "total_amount": 0.96,
                    "line_items": 0.89,
                    "billing_address": 0.87,
                    "shipping_address": 0.87,
                    "incoterms": 0.85,
                    "hs_code": 0.88
                },
                test_category="complex",
                description="International trade invoice with customs information",
                complexity_level="complex",
                source_country="SG",
                currency="USD",
                language="en"
            )
        ])
        
        # Edge cases and challenging invoices
        datasets.extend([
            GoldenInvoiceData(
                id="edge_case_001",
                file_path="test_invoices/edge_case_001.pdf",
                expected_data={
                    "supplier_name": "Handwritten Services",
                    "invoice_number": "HS-2024-007",
                    "invoice_date": "2024-02-15",
                    "due_date": "2024-03-15",
                    "total_amount": 850.00,
                    "currency": "USD",
                    "tax_amount": 68.00,
                    "subtotal": 782.00,
                    "line_items": [
                        {
                            "description": "Consulting Services - Handwritten Invoice",
                            "quantity": 1,
                            "unit_price": 782.00,
                            "total": 782.00
                        }
                    ]
                },
                confidence_thresholds={
                    "supplier_name": 0.85,
                    "invoice_number": 0.88,
                    "total_amount": 0.90,
                    "line_items": 0.82
                },
                test_category="edge_case",
                description="Handwritten invoice with poor quality scan",
                complexity_level="complex",
                source_country="US",
                currency="USD",
                language="en"
            ),
            
            GoldenInvoiceData(
                id="edge_case_002",
                file_path="test_invoices/edge_case_002.pdf",
                expected_data={
                    "supplier_name": "Multi-Language Corp.",
                    "invoice_number": "ML-2024-008",
                    "invoice_date": "2024-02-20",
                    "due_date": "2024-03-20",
                    "total_amount": 12500.00,
                    "currency": "USD",
                    "tax_amount": 1000.00,
                    "subtotal": 11500.00,
                    "line_items": [
                        {
                            "description": "Servicios de Consultoría / Consulting Services",
                            "quantity": 1,
                            "unit_price": 11500.00,
                            "total": 11500.00
                        }
                    ]
                },
                confidence_thresholds={
                    "supplier_name": 0.92,
                    "invoice_number": 0.95,
                    "total_amount": 0.94,
                    "line_items": 0.88
                },
                test_category="edge_case",
                description="Bilingual invoice with mixed languages",
                complexity_level="medium",
                source_country="MX",
                currency="USD",
                language="es"
            )
        ])
        
        return datasets
    
    def _load_ocr_test_cases(self) -> List[Dict[str, Any]]:
        """Load OCR-specific test cases"""
        return [
            {
                "id": "ocr_test_001",
                "description": "High contrast, clear text",
                "expected_accuracy": 0.99,
                "challenges": [],
                "test_type": "baseline"
            },
            {
                "id": "ocr_test_002",
                "description": "Low contrast, faded text",
                "expected_accuracy": 0.85,
                "challenges": ["low_contrast"],
                "test_type": "quality"
            },
            {
                "id": "ocr_test_003",
                "description": "Rotated document",
                "expected_accuracy": 0.90,
                "challenges": ["rotation"],
                "test_type": "orientation"
            },
            {
                "id": "ocr_test_004",
                "description": "Handwritten text",
                "expected_accuracy": 0.75,
                "challenges": ["handwriting"],
                "test_type": "handwriting"
            },
            {
                "id": "ocr_test_005",
                "description": "Multiple languages",
                "expected_accuracy": 0.88,
                "challenges": ["multilingual"],
                "test_type": "language"
            }
        ]
    
    def _load_erp_test_cases(self) -> List[Dict[str, Any]]:
        """Load ERP integration test cases"""
        return [
            {
                "id": "erp_test_001",
                "erp_type": "dynamics_gp",
                "test_data": {
                    "supplier_name": "Test Supplier",
                    "invoice_number": "TEST-001",
                    "total_amount": 1000.00,
                    "currency": "USD",
                    "line_items": [
                        {
                            "description": "Test Item",
                            "quantity": 1,
                            "unit_price": 1000.00,
                            "total": 1000.00,
                            "gl_account": "6000"
                        }
                    ]
                },
                "expected_response": {
                    "status": "success",
                    "erp_document_id": "DOC-001",
                    "posted_at": "2024-01-01T12:00:00Z"
                }
            },
            {
                "id": "erp_test_002",
                "erp_type": "xero",
                "test_data": {
                    "supplier_name": "Xero Test Supplier",
                    "invoice_number": "XERO-001",
                    "total_amount": 2500.00,
                    "currency": "USD",
                    "line_items": [
                        {
                            "description": "Xero Test Item",
                            "quantity": 2,
                            "unit_price": 1250.00,
                            "total": 2500.00,
                            "account_code": "200"
                        }
                    ]
                },
                "expected_response": {
                    "status": "success",
                    "invoice_id": "inv-123",
                    "created_at": "2024-01-01T12:00:00Z"
                }
            }
        ]
    
    def _load_ml_test_cases(self) -> List[Dict[str, Any]]:
        """Load ML model test cases"""
        return [
            {
                "id": "ml_fraud_001",
                "model_type": "fraud_detection",
                "test_data": {
                    "invoice_amount": 50000.00,
                    "supplier_age_days": 30,
                    "payment_terms": 90,
                    "invoice_frequency": 1,
                    "weekend_submission": 1,
                    "amount_deviation": 0.8,
                    "pattern_score": 0.2,
                    "location_risk": 0.9,
                    "time_since_last_hours": 1,
                    "line_count": 1
                },
                "expected_prediction": {
                    "fraud_probability": 0.85,
                    "risk_level": "HIGH"
                }
            },
            {
                "id": "ml_gl_coding_001",
                "model_type": "gl_coding",
                "test_data": {
                    "description": "Office Supplies",
                    "amount": 150.00,
                    "supplier_category": "office_supplies",
                    "invoice_type": "expense"
                },
                "expected_prediction": {
                    "gl_account": "6500",
                    "confidence": 0.92
                }
            },
            {
                "id": "ml_approval_001",
                "model_type": "approval_prediction",
                "test_data": {
                    "invoice_amount": 5000.00,
                    "supplier_score": 0.9,
                    "invoice_age_days": 5,
                    "approval_level": 2,
                    "budget_variance": 0.1,
                    "supplier_approval_rate": 0.95
                },
                "expected_prediction": {
                    "approval_probability": 0.88,
                    "confidence": 0.85
                }
            }
        ]
    
    def get_invoice_dataset(self, dataset_id: str) -> Optional[GoldenInvoiceData]:
        """Get specific invoice dataset by ID"""
        for dataset in self.invoice_datasets:
            if dataset.id == dataset_id:
                return dataset
        return None
    
    def get_datasets_by_category(self, category: str) -> List[GoldenInvoiceData]:
        """Get datasets filtered by category"""
        return [dataset for dataset in self.invoice_datasets if dataset.test_category == category]
    
    def get_datasets_by_complexity(self, complexity: str) -> List[GoldenInvoiceData]:
        """Get datasets filtered by complexity level"""
        return [dataset for dataset in self.invoice_datasets if dataset.complexity_level == complexity]
    
    def get_all_dataset_ids(self) -> List[str]:
        """Get all dataset IDs"""
        return [dataset.id for dataset in self.invoice_datasets]
    
    def validate_ocr_result(self, dataset_id: str, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate OCR result against golden dataset"""
        dataset = self.get_invoice_dataset(dataset_id)
        if not dataset:
            return {"valid": False, "error": f"Dataset {dataset_id} not found"}
        
        validation_results = {}
        overall_score = 0.0
        total_fields = 0
        
        # Validate each expected field
        for field, expected_value in dataset.expected_data.items():
            if field in ocr_result:
                actual_value = ocr_result[field]
                confidence = ocr_result.get("confidence_scores", {}).get(field, 0.0)
                
                # Calculate field accuracy
                field_accuracy = self._calculate_field_accuracy(field, expected_value, actual_value)
                
                # Check confidence threshold
                threshold = dataset.confidence_thresholds.get(field, 0.8)
                meets_threshold = confidence >= threshold
                
                validation_results[field] = {
                    "expected": expected_value,
                    "actual": actual_value,
                    "accuracy": field_accuracy,
                    "confidence": confidence,
                    "threshold": threshold,
                    "meets_threshold": meets_threshold
                }
                
                overall_score += field_accuracy
                total_fields += 1
        
        # Calculate overall validation score
        overall_accuracy = overall_score / total_fields if total_fields > 0 else 0.0
        
        # Determine if validation passes
        passes_validation = overall_accuracy >= 0.95  # 95% accuracy threshold
        
        return {
            "valid": passes_validation,
            "overall_accuracy": overall_accuracy,
            "dataset_id": dataset_id,
            "field_results": validation_results,
            "summary": {
                "total_fields": total_fields,
                "fields_meeting_threshold": len([r for r in validation_results.values() if r["meets_threshold"]]),
                "passes_validation": passes_validation
            }
        }
    
    def _calculate_field_accuracy(self, field: str, expected: Any, actual: Any) -> float:
        """Calculate accuracy for a specific field"""
        if field == "line_items":
            return self._calculate_line_items_accuracy(expected, actual)
        elif isinstance(expected, str) and isinstance(actual, str):
            return self._calculate_string_accuracy(expected, actual)
        elif isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            return self._calculate_numeric_accuracy(expected, actual)
        else:
            return 1.0 if expected == actual else 0.0
    
    def _calculate_line_items_accuracy(self, expected: List[Dict], actual: List[Dict]) -> float:
        """Calculate accuracy for line items"""
        if len(expected) != len(actual):
            return 0.5  # Partial credit for different number of items
        
        total_accuracy = 0.0
        for i, (exp_item, act_item) in enumerate(zip(expected, actual)):
            item_accuracy = 0.0
            item_fields = ["description", "quantity", "unit_price", "total"]
            
            for field in item_fields:
                if field in exp_item and field in act_item:
                    if field in ["quantity", "unit_price", "total"]:
                        item_accuracy += self._calculate_numeric_accuracy(exp_item[field], act_item[field])
                    else:
                        item_accuracy += self._calculate_string_accuracy(exp_item[field], act_item[field])
            
            total_accuracy += item_accuracy / len(item_fields)
        
        return total_accuracy / len(expected)
    
    def _calculate_string_accuracy(self, expected: str, actual: str) -> float:
        """Calculate string accuracy using fuzzy matching"""
        if expected == actual:
            return 1.0
        
        # Simple similarity calculation (in production, use fuzzywuzzy or similar)
        expected_lower = expected.lower().strip()
        actual_lower = actual.lower().strip()
        
        if expected_lower == actual_lower:
            return 0.95
        
        # Calculate character-level similarity
        max_len = max(len(expected_lower), len(actual_lower))
        if max_len == 0:
            return 1.0
        
        matches = sum(1 for a, b in zip(expected_lower, actual_lower) if a == b)
        similarity = matches / max_len
        
        return similarity if similarity > 0.8 else 0.0
    
    def _calculate_numeric_accuracy(self, expected: float, actual: float) -> float:
        """Calculate numeric accuracy with tolerance"""
        if expected == actual:
            return 1.0
        
        # Allow 1% tolerance for numeric values
        tolerance = abs(expected) * 0.01
        difference = abs(expected - actual)
        
        if difference <= tolerance:
            return 1.0
        elif difference <= tolerance * 2:
            return 0.8
        elif difference <= tolerance * 5:
            return 0.5
        else:
            return 0.0

# Global instance
golden_dataset_manager = GoldenDatasetManager()
