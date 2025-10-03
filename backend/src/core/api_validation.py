"""
Advanced API Validation and Serialization
Provides comprehensive validation, serialization, and data transformation utilities
"""
import re
import uuid
from typing import Any, Dict, List, Optional, Union, Type, TypeVar
from datetime import datetime, date, timedelta
from decimal import Decimal
from pydantic import BaseModel, Field, validator, root_validator
from pydantic.types import EmailStr, constr, conint, confloat
from enum import Enum
import json
from sqlalchemy import or_

T = TypeVar('T', bound=BaseModel)

class ValidationError(Exception):
    """Custom validation error with detailed field information"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(message)

class BaseAPIModel(BaseModel):
    """Base model for all API models with common validation and serialization"""
    
            model_config = ConfigDict(
            # Use enum values instead of enum objects
            use_enum_values = True
            # Validate assignment
            validate_assignment = True
            # Allow population by field name
            allow_population_by_field_name = True
            # Use custom encoders
            json_encoders = {
            datetime: lambda v: v.isoformat()
            date: lambda v: v.isoformat()
            uuid.UUID: lambda v: str(v)
            Decimal: lambda v: float(v)
            Enum: lambda v: v.value if hasattr(v, 'value') else str(v)
            }
            # Generate schema with examples
            json_schema_extra = {
            "example": {}
            }
        )
    
    @validator('*', pre=True)
    def validate_uuids(cls, v, field):
        """Validate UUID fields"""
        if field.type_ == uuid.UUID and isinstance(v, str):
            try:
                return uuid.UUID(v)
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
        return v
    
    @validator('*', pre=True)
    def validate_datetimes(cls, v, field):
        """Validate datetime fields"""
        if field.type_ in [datetime, date] and isinstance(v, str):
            try:
                if field.type_ == datetime:
                    return datetime.fromisoformat(v.replace('Z', '+00:00'))
                else:
                    return datetime.fromisoformat(v).date()
            except ValueError:
                raise ValueError(f"Invalid {field.type_.__name__} format: {v}")
        return v
    
    @validator('*', pre=True)
    def validate_decimals(cls, v, field):
        """Validate decimal fields"""
        if field.type_ == Decimal and isinstance(v, (int, float, str)):
            try:
                return Decimal(str(v))
            except (ValueError, TypeError):
                raise ValueError(f"Invalid decimal value: {v}")
        return v

class PaginationParams(BaseAPIModel):
    """Pagination parameters for list endpoints"""
    page: conint(ge=1) = Field(1, description="Page number (1-based)")
    size: conint(ge=1, le=100) = Field(20, description="Items per page (1-100)")
    sort: str = Field("created_at", description="Sort field")
    order: str = Field("desc", description="Sort order (asc/desc)")
    
    @validator('order')
    def validate_order(cls, v):
        if v.lower() not in ['asc', 'desc']:
            raise ValueError("Order must be 'asc' or 'desc'")
        return v.lower()
    
    @validator('sort')
    def validate_sort_field(cls, v):
        # Define allowed sort fields
        allowed_fields = [
            'created_at', 'updated_at', 'id', 'name', 'email', 
            'status', 'amount', 'invoice_date', 'due_date'
        ]
        if v not in allowed_fields:
            raise ValueError(f"Invalid sort field. Allowed: {', '.join(allowed_fields)}")
        return v

class FilterParams(BaseAPIModel):
    """Filter parameters for list endpoints"""
    search: Optional[str] = Field(None, description="Search term")
    status: Optional[str] = Field(None, description="Filter by status")
    date_from: Optional[date] = Field(None, description="Filter from date")
    date_to: Optional[date] = Field(None, description="Filter to date")
    amount_min: Optional[confloat(ge=0)] = Field(None, description="Minimum amount")
    amount_max: Optional[confloat(ge=0)] = Field(None, description="Maximum amount")
    
    @root_validator
    def validate_date_range(cls, values):
        date_from = values.get('date_from')
        date_to = values.get('date_to')
        if date_from and date_to and date_from > date_to:
            raise ValueError("date_from must be before date_to")
        return values
    
    @root_validator
    def validate_amount_range(cls, values):
        amount_min = values.get('amount_min')
        amount_max = values.get('amount_max')
        if amount_min and amount_max and amount_min > amount_max:
            raise ValueError("amount_min must be less than amount_max")
        return values

class CompanyValidationMixin(BaseAPIModel):
    """Validation mixin for company-related models"""
    
    @validator('name')
    def validate_company_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Company name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Company name must be less than 100 characters")
        return v.strip()
    
    @validator('email')
    def validate_company_email(cls, v):
        if not v:
            raise ValueError("Company email is required")
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()

class UserValidationMixin(BaseAPIModel):
    """Validation mixin for user-related models"""
    
    @validator('email')
    def validate_user_email(cls, v):
        if not v:
            raise ValueError("Email is required")
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()
    
    @validator('password')
    def validate_password(cls, v):
        if not v:
            raise ValueError("Password is required")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must be less than 128 characters")
        # Check for at least one uppercase, lowercase, digit, and special character
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError("Name cannot be empty")
        if len(v) > 50:
            raise ValueError("Name must be less than 50 characters")
        return v.strip()

class InvoiceValidationMixin(BaseAPIModel):
    """Validation mixin for invoice-related models"""
    
    @validator('invoice_number')
    def validate_invoice_number(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError("Invoice number is required")
        if len(v) > 100:
            raise ValueError("Invoice number must be less than 100 characters")
        return v.strip()
    
    @validator('supplier_name')
    def validate_supplier_name(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError("Supplier name is required")
        if len(v) > 200:
            raise ValueError("Supplier name must be less than 200 characters")
        return v.strip()
    
    @validator('total_amount')
    def validate_total_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError("Total amount cannot be negative")
        return v
    
    @validator('invoice_date', 'due_date')
    def validate_dates(cls, v):
        if v and v > date.today() + timedelta(days=365):
            raise ValueError("Date cannot be more than 1 year in the future")
        return v

class ERPValidationMixin(BaseAPIModel):
    """Validation mixin for ERP-related models"""
    
    @validator('connection_config')
    def validate_connection_config(cls, v):
        if not v:
            raise ValueError("Connection configuration is required")
        if not isinstance(v, dict):
            raise ValueError("Connection configuration must be a dictionary")
        return v
    
    @validator('erp_type')
    def validate_erp_type(cls, v):
        allowed_types = ['dynamics_gp', 'dynamics_365_bc', 'xero', 'quickbooks']
        if v not in allowed_types:
            raise ValueError(f"Invalid ERP type. Allowed: {', '.join(allowed_types)}")
        return v

class DataSerializer:
    """Advanced data serialization utilities"""
    
    @staticmethod
    def serialize_model(model: BaseModel, exclude_none: bool = True) -> Dict[str, Any]:
        """Serialize a Pydantic model to dictionary"""
        data = model.dict(exclude_none=exclude_none)
        return DataSerializer._convert_types(data)
    
    @staticmethod
    def serialize_models(models: List[BaseModel], exclude_none: bool = True) -> List[Dict[str, Any]]:
        """Serialize a list of Pydantic models"""
        return [DataSerializer.serialize_model(model, exclude_none) for model in models]
    
    @staticmethod
    def serialize_sqlalchemy_model(model, exclude_fields: List[str] = None) -> Dict[str, Any]:
        """Serialize a SQLAlchemy model to dictionary"""
        exclude_fields = exclude_fields or []
        data = {}
        
        for column in model.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(model, column.name)
                data[column.name] = DataSerializer._convert_value(value)
        
        return data
    
    @staticmethod
    def serialize_sqlalchemy_models(models: List, exclude_fields: List[str] = None) -> List[Dict[str, Any]]:
        """Serialize a list of SQLAlchemy models"""
        return [DataSerializer.serialize_sqlalchemy_model(model, exclude_fields) for model in models]
    
    @staticmethod
    def _convert_types(data: Any) -> Any:
        """Convert types for JSON serialization"""
        if isinstance(data, dict):
            return {key: DataSerializer._convert_types(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [DataSerializer._convert_types(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, date):
            return data.isoformat()
        elif isinstance(data, uuid.UUID):
            return str(data)
        elif isinstance(data, Decimal):
            return float(data)
        elif isinstance(data, Enum):
            return data.value if hasattr(data, 'value') else str(data)
        else:
            return data
    
    @staticmethod
    def _convert_value(value: Any) -> Any:
        """Convert a single value for serialization"""
        if value is None:
            return None
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, Enum):
            return value.value if hasattr(value, 'value') else str(value)
        else:
            return value

class DataValidator:
    """Advanced data validation utilities"""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that all required fields are present"""
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    @staticmethod
    def validate_field_types(data: Dict[str, Any], field_types: Dict[str, Type]) -> None:
        """Validate field types"""
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    raise ValidationError(
                        f"Field '{field}' must be of type {expected_type.__name__}",
                        field=field,
                        value=data[field]
                    )
    
    @staticmethod
    def validate_string_length(data: Dict[str, Any], field_lengths: Dict[str, int]) -> None:
        """Validate string field lengths"""
        for field, max_length in field_lengths.items():
            if field in data and data[field] is not None:
                if len(str(data[field])) > max_length:
                    raise ValidationError(
                        f"Field '{field}' exceeds maximum length of {max_length}",
                        field=field,
                        value=data[field]
                    )
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone_format(phone: str) -> bool:
        """Validate phone number format"""
        pattern = r'^\+?[\d\s\-\(\)]{10,}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_url_format(url: str) -> bool:
        """Validate URL format"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))

class QueryBuilder:
    """Advanced query building utilities"""
    
    @staticmethod
    def build_pagination_query(query, pagination: PaginationParams):
        """Build pagination query"""
        offset = (pagination.page - 1) * pagination.size
        return query.offset(offset).limit(pagination.size)
    
    @staticmethod
    def build_sort_query(query, sort_field: str, order: str):
        """Build sort query"""
        if hasattr(query.column_descriptions[0]['entity'], sort_field):
            sort_column = getattr(query.column_descriptions[0]['entity'], sort_field)
            if order.lower() == 'desc':
                return query.order_by(sort_column.desc())
            else:
                return query.order_by(sort_column.asc())
        return query
    
    @staticmethod
    def build_filter_query(query, filters: FilterParams, model_class):
        """Build filter query"""
        if filters.search:
            # Add search across multiple fields
            search_terms = filters.search.split()
            for term in search_terms:
                query = query.filter(
                    or_(
                        model_class.name.ilike(f'%{term}%'),
                        model_class.email.ilike(f'%{term}%'),
                        model_class.description.ilike(f'%{term}%')
                    )
                )
        
        if filters.status:
            query = query.filter(model_class.status == filters.status)
        
        if filters.date_from:
            query = query.filter(model_class.created_at >= filters.date_from)
        
        if filters.date_to:
            query = query.filter(model_class.created_at <= filters.date_to)
        
        if filters.amount_min is not None:
            query = query.filter(model_class.amount >= filters.amount_min)
        
        if filters.amount_max is not None:
            query = query.filter(model_class.amount <= filters.amount_max)
        
        return query

def validate_api_request(data: Dict[str, Any], model_class: Type[T]) -> T:
    """Validate API request data against a Pydantic model"""
    try:
        return model_class(**data)
    except Exception as e:
        raise ValidationError(f"Request validation failed: {str(e)}")

def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize input data to prevent injection attacks"""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remove potentially dangerous characters
            sanitized[key] = re.sub(r'[<>"\']', '', value).strip()
        elif isinstance(value, dict):
            sanitized[key] = sanitize_input(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_input(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value
    return sanitized
