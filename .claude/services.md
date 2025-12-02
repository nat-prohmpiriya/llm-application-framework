# Service Layer Instructions

## Service Pattern

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundError
from app.core.telemetry import traced

@traced()
async def get_user(db: AsyncSession, user_id: int) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user

@traced()
async def create_user(db: AsyncSession, data: UserCreate) -> User:
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

## Rules

1. Use `@traced()` decorator on all service functions
2. Raise domain exceptions (not HTTPException)
3. No HTTP knowledge (no Request, Response)
4. Accept `AsyncSession` as first parameter

## Database Operations

```python
# Get by ID
user = await db.get(User, user_id)

# Query with filter
result = await db.execute(
    select(User).where(User.email == email)
)
user = result.scalar_one_or_none()

# Create
db.add(user)
await db.commit()
await db.refresh(user)

# Update
user.email = new_email
await db.commit()

# Delete
await db.delete(user)
await db.commit()
```

## Exception Handling

```python
from app.core.exceptions import NotFoundError, DuplicateError

raise NotFoundError("User", user_id)
raise DuplicateError("User", "email", email)
raise InvalidCredentialsError()
```
