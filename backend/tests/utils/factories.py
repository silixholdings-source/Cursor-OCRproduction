"""
Factory classes for generating test data
"""
import uuid
from datetime import datetime, timedelta
from factory import Factory, Faker, SubFactory, LazyFunction
from factory.fuzzy import FuzzyChoice, FuzzyDecimal, FuzzyInteger
from sqlalchemy.orm import Session

from src.models.user import User, UserRole, UserStatus
from src.models.company import Company, CompanyStatus, CompanyTier
from src.models.invoice import Invoice, InvoiceStatus, InvoiceType
from src.models.audit import AuditLog, AuditAction

class CompanyFactory(Factory):
    """Factory for creating Company instances"""
    class Meta:
        model = Company
    
    id = LazyFunction(uuid.uuid4)
    name = Faker('company')
    display_name = Faker('company')
    description = Faker('text', max_nb_chars=200)
    email = Faker('company_email')
    phone = Faker('phone_number')
    website = Faker('url')
    address_line1 = Faker('street_address')
    city = Faker('city')
    state = Faker('state')
    postal_code = Faker('postcode')
    country = Faker('country')
    tax_id = Faker('ssn')
    industry = FuzzyChoice(['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail'])
    company_size = FuzzyChoice(['1-10', '11-50', '51-200', '201-1000', '1000+'])
    status = FuzzyChoice([CompanyStatus.ACTIVE, CompanyStatus.TRIAL])
    tier = FuzzyChoice([CompanyTier.GROWTH, CompanyTier.PROFESSIONAL, CompanyTier.ENTERPRISE])
    subscription_id = Faker('uuid4')
    trial_ends_at = LazyFunction(lambda: datetime.utcnow() + timedelta(days=30))
    subscription_ends_at = None
    settings = LazyFunction(dict)
    features = LazyFunction(dict)
    max_users = FuzzyInteger(5, 100)
    max_storage_gb = FuzzyInteger(10, 1000)
    max_invoices_per_month = FuzzyInteger(100, 10000)

class UserFactory(Factory):
    """Factory for creating User instances"""
    class Meta:
        model = User
    
    id = LazyFunction(uuid.uuid4)
    email = Faker('email')
    username = Faker('user_name')
    hashed_password = Faker('sha256')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    phone = Faker('phone_number')
    avatar_url = Faker('image_url')
    company = SubFactory(CompanyFactory)
    company_id = LazyFunction(lambda: CompanyFactory().id)
    role = FuzzyChoice([UserRole.USER, UserRole.MANAGER, UserRole.ADMIN, UserRole.OWNER])
    status = FuzzyChoice([UserStatus.ACTIVE, UserStatus.PENDING_VERIFICATION])
    is_email_verified = FuzzyChoice([True, False])
    is_2fa_enabled = False
    last_login = None
    failed_login_attempts = 0
    locked_until = None

class InvoiceFactory(Factory):
    """Factory for creating Invoice instances"""
    class Meta:
        model = Invoice
    
    id = LazyFunction(uuid.uuid4)
    invoice_number = Faker('uuid4')
    supplier_name = Faker('company')
    supplier_email = Faker('company_email')
    supplier_phone = Faker('phone_number')
    supplier_address = Faker('address')
    invoice_date = Faker('date_this_year')
    due_date = LazyFunction(lambda: datetime.utcnow() + timedelta(days=30))
    total_amount = FuzzyDecimal(100.0, 10000.0, 2)
    currency = FuzzyChoice(['USD', 'EUR', 'GBP', 'CAD', 'AUD'])
    tax_amount = LazyFunction(lambda self: round(self.total_amount * 0.08, 2))
    tax_rate = 0.08
    subtotal = LazyFunction(lambda self: self.total_amount)
    total_with_tax = LazyFunction(lambda self: self.total_amount + self.tax_amount)
    status = FuzzyChoice([InvoiceStatus.DRAFT, InvoiceStatus.PENDING_APPROVAL, InvoiceStatus.APPROVED])
    type = FuzzyChoice([InvoiceType.INVOICE, InvoiceType.CREDIT_MEMO, InvoiceType.DEBIT_MEMO])
    notes = Faker('text', max_nb_chars=500)
    company = SubFactory(CompanyFactory)
    company_id = LazyFunction(lambda: CompanyFactory().id)
    created_by = SubFactory(UserFactory)
    created_by_id = LazyFunction(lambda: UserFactory().id)
    approved_by = None
    approved_by_id = None
    approved_at = None
    posted_to_erp = False
    erp_document_id = None
    erp_posting_date = None
    ocr_data = LazyFunction(dict)
    workflow_data = LazyFunction(dict)

class AuditLogFactory(Factory):
    """Factory for creating AuditLog instances"""
    class Meta:
        model = AuditLog
    
    id = LazyFunction(uuid.uuid4)
    action = FuzzyChoice([AuditAction.CREATE, AuditAction.UPDATE, AuditAction.DELETE, AuditAction.APPROVE])
    resource_type = FuzzyChoice(['Invoice', 'User', 'Company', 'Approval'])
    resource_id = LazyFunction(uuid.uuid4)
    user = SubFactory(UserFactory)
    user_id = LazyFunction(lambda: UserFactory().id)
    company = SubFactory(CompanyFactory)
    company_id = LazyFunction(lambda: CompanyFactory().id)
    details = LazyFunction(dict)
    ip_address = Faker('ipv4')
    user_agent = Faker('user_agent')
    timestamp = Faker('date_time_this_year')

def create_test_company(db: Session, **kwargs) -> Company:
    """Create a test company in the database"""
    company_data = CompanyFactory.build(**kwargs)
    company = Company(**company_data.__dict__)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

def create_test_user(db: Session, company_id: uuid.UUID, **kwargs) -> User:
    """Create a test user in the database"""
    user_data = UserFactory.build(company_id=company_id, **kwargs)
    user = User(**user_data.__dict__)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_test_invoice(db: Session, company_id: uuid.UUID, created_by_id: uuid.UUID, **kwargs) -> Invoice:
    """Create a test invoice in the database"""
    invoice_data = InvoiceFactory.build(
        company_id=company_id,
        created_by_id=created_by_id,
        **kwargs
    )
    invoice = Invoice(**invoice_data.__dict__)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

def create_test_audit_log(db: Session, user_id: uuid.UUID, company_id: uuid.UUID, **kwargs) -> AuditLog:
    """Create a test audit log in the database"""
    audit_data = AuditLogFactory.build(
        user_id=user_id,
        company_id=company_id,
        **kwargs
    )
    audit_log = AuditLog(**audit_data.__dict__)
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log
