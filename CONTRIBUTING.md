# Contributing to AI ERP SaaS

Thank you for your interest in contributing to the AI ERP SaaS project! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Commit Message Convention](#commit-message-convention)
- [Branching Model](#branching-model)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Node.js 18+ and npm 9+
- Python 3.11+
- Docker and Docker Compose
- Git

### Setup Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/ai-erp-saas-app.git
   cd ai-erp-saas-app
   ```

2. **Install dependencies**
   ```bash
   make setup
   ```

3. **Start development services**
   ```bash
   make start-dev
   ```

4. **Run tests to verify setup**
   ```bash
   make test
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following the established patterns
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
make test

# Run specific service tests
make test-backend
make test-web
make test-mobile

# Run with coverage
make test-coverage
```

### 4. Commit Your Changes

Follow the [commit message convention](#commit-message-convention).

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

## Code Standards

### Backend (Python)

- **Style**: Follow PEP 8 and use Black for formatting
- **Type Hints**: Use type hints for all function parameters and return values
- **Documentation**: Use docstrings for all public functions and classes
- **Imports**: Use absolute imports, organize with isort

```python
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """Create a new user."""
    # Implementation here
    pass
```

### Frontend (React/TypeScript)

- **Style**: Use Prettier for formatting, ESLint for linting
- **Components**: Use functional components with hooks
- **TypeScript**: Use strict mode, define interfaces for all props
- **Testing**: Use React Testing Library for component tests

```typescript
import React from 'react';
import { useQuery } from 'react-query';
import { Box, Typography } from '@mui/material';

interface User {
  id: number;
  name: string;
  email: string;
}

interface UserListProps {
  onUserSelect: (user: User) => void;
}

export const UserList: React.FC<UserListProps> = ({ onUserSelect }) => {
  const { data: users, isLoading } = useQuery<User[]>('users', fetchUsers);

  if (isLoading) return <Typography>Loading...</Typography>;

  return (
    <Box>
      {users?.map(user => (
        <div key={user.id} onClick={() => onUserSelect(user)}>
          {user.name}
        </div>
      ))}
    </Box>
  );
};
```

### Mobile (React Native)

- **Style**: Follow React Native best practices
- **Navigation**: Use React Navigation for routing
- **State Management**: Use Zustand for global state
- **Testing**: Use React Native Testing Library

## Testing

### Test Requirements

- **Coverage**: Minimum 85% code coverage
- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test API endpoints and database operations
- **E2E Tests**: Test complete user workflows

### Running Tests

```bash
# All tests
make test

# Specific service tests
make test-backend
make test-web
make test-mobile

# With coverage
make test-coverage
```

### Writing Tests

#### Backend Tests

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.main import app

client = TestClient(app)

class TestUserEndpoints:
    def test_create_user_success(self):
        """Test successful user creation"""
        user_data = {"name": "Test User", "email": "test@example.com"}
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == user_data["name"]
        assert data["email"] == user_data["email"]
```

#### Frontend Tests

```typescript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { UserList } from './UserList';

describe('UserList Component', () => {
  const mockUsers = [
    { id: 1, name: 'John Doe', email: 'john@example.com' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
  ];

  test('renders user list', () => {
    render(<UserList users={mockUsers} onUserSelect={jest.fn()} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });
});
```

## Pull Request Process

### PR Checklist

Before submitting a PR, ensure:

- [ ] **Tests Pass**: All tests pass locally and in CI
- [ ] **Coverage**: Code coverage is at least 85%
- [ ] **Linting**: Code passes all linting checks
- [ ] **Documentation**: Updated API docs and README if needed
- [ ] **Migration**: Database migrations included if schema changed
- [ ] **Breaking Changes**: Documented any breaking changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated
- [ ] All tests pass locally

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Breaking changes documented

## Screenshots (if applicable)
Add screenshots for UI changes

## Additional Notes
Any additional information
```

## Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Build process or auxiliary tool changes

### Examples

```bash
feat(auth): add JWT authentication system

feat(api): implement user CRUD endpoints

fix(web): resolve navigation issue in mobile view

docs: update API documentation

test(backend): add integration tests for user service

chore: update Docker configuration
```

## Branching Model

### Main Branches

- **main**: Production-ready code
- **develop**: Integration branch for features

### Supporting Branches

- **feature/***: New features
- **bugfix/***: Bug fixes
- **hotfix/***: Urgent production fixes
- **release/***: Release preparation

### Branch Naming

```
feature/user-authentication
bugfix/login-validation
hotfix/security-vulnerability
release/v1.2.0
```

## Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Environment**: OS, Node.js version, Python version
2. **Steps to Reproduce**: Clear, step-by-step instructions
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Screenshots**: If applicable
6. **Logs**: Error messages and stack traces

### Feature Requests

For feature requests:

1. **Description**: Clear description of the feature
2. **Use Case**: Why this feature is needed
3. **Proposed Solution**: How you think it should work
4. **Alternatives**: Any alternatives you've considered

## Getting Help

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the project documentation first

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to AI ERP SaaS! 🚀
