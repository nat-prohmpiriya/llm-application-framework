---
applyTo: "backend/app/services/**"
---

# Service Layer Instructions

## Service Responsibilities

Services contain **business logic** and **database operations**.
Services should NOT know about HTTP (no Request, Response, status codes).

## Service Pattern

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.exceptions import NotFoundError, DuplicateError
from app.core.telemetry import traced

@traced()
async def get_user(db: AsyncSession, user_id: int) -> User:
    """Get user by ID or raise NotFoundError."""
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user

@traced()
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email, returns None if not found."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

@traced()
async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """Create new user. Raises DuplicateError if email exists."""
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise DuplicateError("User", "email", data.email)
    
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        username=data.username,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@traced()
async def update_user(db: AsyncSession, user_id: int, data: UserUpdate) -> User:
    """Update existing user."""
    user = await get_user(db, user_id)
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return user
```

## @traced Decorator

Use `@traced()` on all service functions for observability:

```python
from app.core.telemetry import traced

@traced()
async def process_order(db: AsyncSession, order_id: int) -> Order:
    # Automatically tracks: input args, return value, timing
    ...

@traced(skip_input=True)  # For functions with sensitive data
async def authenticate(db: AsyncSession, email: str, password: str) -> User:
    ...
```

## Database Operations

### Fetching Data

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Single by ID
user = await db.get(User, user_id)

# Single by condition
result = await db.execute(
    select(User).where(User.email == email)
)
user = result.scalar_one_or_none()

# Multiple with filter
result = await db.execute(
    select(User)
    .where(User.is_active == True)
    .order_by(User.created_at.desc())
    .limit(10)
)
users = result.scalars().all()

# With eager loading
result = await db.execute(
    select(User)
    .options(selectinload(User.orders))
    .where(User.id == user_id)
)
```

### Creating Data

```python
user = User(email=email, username=username)
db.add(user)
await db.commit()
await db.refresh(user)  # Get auto-generated fields
return user
```

### Updating Data

```python
user = await get_user(db, user_id)
user.email = new_email
await db.commit()
await db.refresh(user)
```

### Deleting Data

```python
user = await get_user(db, user_id)
await db.delete(user)
await db.commit()
```

## Exception Handling

Raise custom exceptions, let routes/middleware handle HTTP conversion:

```python
from app.core.exceptions import (
    NotFoundError,
    DuplicateError,
    InvalidCredentialsError,
    PermissionDeniedError,
)

# Resource not found
raise NotFoundError("User", user_id)

# Duplicate entry
raise DuplicateError("User", "email", email)

# Auth failures
raise InvalidCredentialsError()

# Permission issues
raise PermissionDeniedError("Cannot delete other user's project")
```

## No HTTP Knowledge

Services should NEVER:
- Import from `fastapi` (except exceptions)
- Use HTTPException
- Return HTTP status codes
- Access Request objects

```python
# ❌ Bad - HTTP in service
from fastapi import HTTPException, status

async def get_user(db, user_id):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user

# ✅ Good - Domain exception
from app.core.exceptions import NotFoundError

async def get_user(db, user_id):
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user
```
