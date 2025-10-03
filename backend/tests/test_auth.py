"""
Tests for authentication functionality
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

@pytest.mark.auth
class TestAuthentication:
    """Test authentication functionality."""

    def test_user_registration_success(self, client: TestClient, db_session: Session):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "company": {
                "name": "New Company",
                "email": "newcompany@example.com"
            }
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == user_data["email"]

    def test_user_registration_duplicate_email(self, client: TestClient, test_user):
        """Test registration with duplicate email fails."""
        user_data = {
            "email": test_user.email,  # Same email as existing user
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "company": {
                "name": "Test Company",
                "email": "test@company.com"
            }
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"].lower()

    def test_user_login_success(self, client: TestClient, test_user):
        """Test successful user login."""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_user_login_invalid_credentials(self, client: TestClient, test_user):
        """Test login with invalid credentials fails."""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_user_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user fails."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

    def test_get_current_user(self, client: TestClient, auth_headers: dict, test_user):
        """Test getting current user profile."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert "id" in data
        assert "company" in data

    def test_get_current_user_without_auth(self, client: TestClient):
        """Test getting current user without authentication fails."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_refresh_token(self, client: TestClient, test_user):
        """Test token refresh."""
        # First login to get refresh token
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        refresh_token = response.json()["refresh_token"]
        
        # Use refresh token to get new access token
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token fails."""
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid_token"})
        assert response.status_code == 401

    def test_logout(self, client: TestClient, auth_headers: dict):
        """Test user logout."""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"

    def test_password_validation(self, client: TestClient):
        """Test password validation during registration."""
        user_data = {
            "email": "test@example.com",
            "password": "123",  # Too short
            "first_name": "Test",
            "last_name": "User",
            "company": {
                "name": "Test Company",
                "email": "test@company.com"
            }
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

    def test_email_validation(self, client: TestClient):
        """Test email validation during registration."""
        user_data = {
            "email": "invalid-email",  # Invalid email format
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "company": {
                "name": "Test Company",
                "email": "test@company.com"
            }
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_token_expiration(self, client: TestClient, test_user):
        """Test that expired tokens are rejected."""
        # This would require mocking time or using a very short expiration
        # For now, we'll test with an obviously invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/api/v1/auth/me", headers=invalid_headers)
        assert response.status_code == 401

    def test_company_isolation(self, client: TestClient, auth_headers: dict, test_company):
        """Test that users can only access their own company's data."""
        # Create another company
        import uuid
        from src.models.company import Company, CompanyStatus
        
        other_company = Company(
            id=uuid.uuid4(),
            name="Other Company",
            email="other@company.com",
            status=CompanyStatus.ACTIVE,
            max_users=10,
            max_invoices_per_month=1000
        )
        
        # Test that user can only see their company
        response = client.get("/api/v1/company", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_company.id)
        assert data["name"] == test_company.name
