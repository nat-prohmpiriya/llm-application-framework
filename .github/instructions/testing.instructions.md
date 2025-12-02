---
applyTo: "**/test*"
---

# Testing Instructions

## Backend Testing (pytest)

### Test Structure

```
backend/tests/
├── conftest.py              # Shared fixtures
├── factories.py             # Factory Boy factories
├── unit/
│   ├── test_services/
│   │   └── test_user.py
│   └── test_utils/
├── integration/
│   ├── test_routes/
│   │   ├── test_auth.py
│   │   └── test_users.py
│   └── conftest.py          # Test DB setup
```

### Test File Pattern

```python
import pytest
from unittest.mock import AsyncMock, patch

from app.services import user_service
from app.schemas.user import UserCreate
from app.core.exceptions import NotFoundError


class TestGetUser:
    """Tests for user_service.get_user"""
    
    @pytest.mark.asyncio
    async def test_returns_user_when_exists(self, db_session, user_factory):
        # Arrange
        user = await user_factory.create()
        
        # Act
        result = await user_service.get_user(db_session, user.id)
        
        # Assert
        assert result.id == user.id
        assert result.email == user.email

    @pytest.mark.asyncio
    async def test_raises_not_found_when_missing(self, db_session):
        # Act & Assert
        with pytest.raises(NotFoundError) as exc:
            await user_service.get_user(db_session, 99999)
        
        assert "User" in str(exc.value)


class TestCreateUser:
    """Tests for user_service.create_user"""
    
    @pytest.mark.asyncio
    async def test_creates_user_with_valid_data(self, db_session):
        # Arrange
        data = UserCreate(
            email="test@example.com",
            password="securepassword123",
            username="testuser",
        )
        
        # Act
        result = await user_service.create_user(db_session, data)
        
        # Assert
        assert result.email == data.email
        assert result.username == data.username
        assert result.id is not None
```

### Test Naming Convention

```python
# Pattern: test_<action>_<expected_outcome>_<condition>

def test_get_user_returns_user_when_exists():
    ...

def test_get_user_raises_not_found_when_missing():
    ...

def test_create_user_hashes_password():
    ...

def test_login_fails_with_wrong_password():
    ...
```

### Fixtures (conftest.py)

```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.base import Base

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def db_session():
    """Create a fresh database session for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
```

### Mocking External Services

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_chat_calls_llm_service():
    mock_llm = AsyncMock(return_value="AI response")
    
    with patch("app.providers.llm.complete", mock_llm):
        result = await chat_service.send_message("Hello")
    
    mock_llm.assert_called_once()
    assert result == "AI response"
```

## Frontend Testing (vitest)

### Component Test Pattern

```typescript
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import UserCard from './UserCard.svelte';

describe('UserCard', () => {
  it('renders user name', () => {
    render(UserCard, {
      props: {
        user: { name: 'John Doe', email: 'john@example.com' },
      },
    });
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const onClick = vi.fn();
    
    render(UserCard, {
      props: {
        user: { name: 'John', email: 'john@example.com' },
        onClick,
      },
    });
    
    await fireEvent.click(screen.getByRole('button'));
    
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```

## Test Commands

### Backend
```bash
cd backend
uv run pytest                        # Run all tests
uv run pytest -v                     # Verbose output
uv run pytest --cov=app              # With coverage
uv run pytest tests/unit/            # Only unit tests
uv run pytest -k "test_create"       # Filter by name
```

### Frontend
```bash
cd frontend
npm run test                         # Run all tests
npm run test:coverage                # With coverage
npm run test -- --watch              # Watch mode
```

## Coverage Target

- **Services**: 90%+
- **Routes**: 80%+
- **Utils**: 90%+
- **Overall**: 80%+
