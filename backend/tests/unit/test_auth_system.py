import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, UTC
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.auth import AuthManager
from src.models.user import User, UserRole, UserStatus
from src.models.company import Company, CompanyStatus, CompanyTier
from src.schemas.auth import UserLoginRequest, UserRegisterRequest

class TestAuthManager:
    """Test authentication manager functionality"""
    
    def test_verify_password(self):
        """Test password verification"""
        password = "testpassword123"
        hashed = AuthManager.get_password_hash(password)
        
        assert AuthManager.verify_password(password, hashed) is True
        assert AuthManager.verify_password("wrongpassword", hashed) is False
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = AuthManager.create_access_token(data)
        
        assert token is not None
        assert len(token) > 0
        
        # Verify token can be decoded
        payload = AuthManager.verify_token(token)
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = AuthManager.create_refresh_token(data)
        
        assert token is not None
        assert len(token) > 0
        
        # Verify token can be decoded
        payload = AuthManager.verify_token(token)
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "refresh"
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            AuthManager.verify_token("invalid.token.here")
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    def test_authenticate_user_success(self, db_session: Session):
        """Test successful user authentication"""
        # Create test company
        company = Company(
            name="Test Company",
            email="test@company.com",
            status=CompanyStatus.ACTIVE,
            tier=CompanyTier.PROFESSIONAL
        )
        db_session.add(company)
        db_session.commit()
        
        # Create test user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=AuthManager.get_password_hash("testpassword123"),
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test authentication
        authenticated_user = AuthManager.authenticate_user(
            db_session, "test@example.com", "testpassword123"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert authenticated_user.email == "test@example.com"
    
    def test_authenticate_user_wrong_password(self, db_session: Session):
        """Test user authentication with wrong password"""
        # Create test company
        company = Company(
            name="Test Company",
            email="test@company.com",
            status=CompanyStatus.ACTIVE,
            tier=CompanyTier.PROFESSIONAL
        )
        db_session.add(company)
        db_session.commit()
        
        # Create test user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=AuthManager.get_password_hash("testpassword123"),
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test authentication with wrong password
        authenticated_user = AuthManager.authenticate_user(
            db_session, "test@example.com", "wrongpassword"
        )
        
        assert authenticated_user is None
    
    def test_authenticate_user_inactive(self, db_session: Session):
        """Test authentication with inactive user"""
        # Create test company
        company = Company(
            name="Test Company",
            email="test@company.com",
            status=CompanyStatus.ACTIVE,
            tier=CompanyTier.PROFESSIONAL
        )
        db_session.add(company)
        db_session.commit()
        
        # Create inactive user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=AuthManager.get_password_hash("testpassword123"),
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.INACTIVE
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test authentication
        authenticated_user = AuthManager.authenticate_user(
            db_session, "test@example.com", "testpassword123"
        )
        
        assert authenticated_user is None
    
    def test_authenticate_user_locked(self, db_session: Session):
        """Test authentication with locked user"""
        # Create test company
        company = Company(
            name="Test Company",
            email="test@company.com",
            status=CompanyStatus.ACTIVE,
            tier=CompanyTier.PROFESSIONAL
        )
        db_session.add(company)
        db_session.commit()
        
        # Create locked user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=AuthManager.get_password_hash("testpassword123"),
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            locked_until=datetime.now(UTC) + timedelta(hours=1)
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test authentication
        authenticated_user = AuthManager.authenticate_user(
            db_session, "test@example.com", "testpassword123"
        )
        
        assert authenticated_user is None
    
    def test_authenticate_user_not_found(self, db_session: Session):
        """Test authentication with non-existent user"""
        authenticated_user = AuthManager.authenticate_user(
            db_session, "nonexistent@example.com", "testpassword123"
        )
        
        assert authenticated_user is None

class TestUserModel:
    """Test user model functionality"""
    
    def test_user_properties(self, db_session: Session):
        """Test user model properties"""
        # Create test company
        company = Company(
            name="Test Company",
            email="test@company.com",
            status=CompanyStatus.ACTIVE,
            tier=CompanyTier.PROFESSIONAL
        )
        db_session.add(company)
        db_session.commit()
        
        # Create test user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_locked is False
    
    def test_user_locked_property(self, db_session: Session):
        """Test user locked property"""
        # Create test company
        company = Company(
            name="Test Company",
            email="test@company.com",
            status=CompanyStatus.ACTIVE,
            tier=CompanyTier.PROFESSIONAL
        )
        db_session.add(company)
        db_session.commit()
        
        # Create locked user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            locked_until=datetime.now(UTC) + timedelta(hours=1)
        )
        
        assert user.is_locked is True
    
    def test_user_can_access_company(self, db_session: Session):
        """Test user company access control"""
        # Create test company
        company = Company(
            name="Test Company",
            email="test@company.com",
            status=CompanyStatus.ACTIVE,
            tier=CompanyTier.PROFESSIONAL
        )
        db_session.add(company)
        db_session.commit()
        
        # Create test user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        
        assert user.can_access_company(company.id) is True
        assert user.can_access_company("different-company-id") is False













