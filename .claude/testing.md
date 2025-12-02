# Testing Instructions

## Backend (pytest)

### Test Structure
```
tests/
├── conftest.py          # Fixtures
├── unit/
│   └── test_services/
└── integration/
    └── test_routes/
```

### Test Pattern

```python
import pytest
from app.services import user_service
from app.core.exceptions import NotFoundError

class TestGetUser:
    @pytest.mark.asyncio
    async def test_returns_user_when_exists(self, db_session, user_factory):
        user = await user_factory.create()
        result = await user_service.get_user(db_session, user.id)
        assert result.id == user.id

    @pytest.mark.asyncio
    async def test_raises_not_found_when_missing(self, db_session):
        with pytest.raises(NotFoundError):
            await user_service.get_user(db_session, 99999)
```

### Naming Convention
```python
def test_get_user_returns_user_when_exists():
def test_get_user_raises_not_found_when_missing():
def test_create_user_hashes_password():
```

### Commands
```bash
uv run pytest                    # All tests
uv run pytest -v                 # Verbose
uv run pytest --cov=app          # Coverage
uv run pytest tests/unit/        # Unit only
```

## Frontend (vitest)

```typescript
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';

describe('UserCard', () => {
  it('renders user name', () => {
    render(UserCard, { props: { user: { name: 'John' } } });
    expect(screen.getByText('John')).toBeInTheDocument();
  });
});
```

## Coverage Target
- Services: 90%+
- Routes: 80%+
- Overall: 80%+
