---
applyTo: "**/*.py"
---

# Python Code Instructions

## Python Version
Use Python 3.12+ features.

## Type Hints (Required)

Always add type hints to all functions:

```python
# ✅ Good
async def get_user(user_id: int, db: AsyncSession) -> User | None:
    ...

def calculate_total(items: list[dict[str, Any]]) -> float:
    ...

# ❌ Bad - Missing type hints
async def get_user(user_id, db):
    ...
```

## Modern Type Syntax

Use Python 3.10+ union syntax:

```python
# ✅ Good
def process(name: str | None = None) -> dict[str, Any]:
    ...

# ❌ Bad (legacy)
from typing import Optional, Dict, Any
def process(name: Optional[str] = None) -> Dict[str, Any]:
    ...
```

## Async/Await

Use async for all I/O operations:

```python
# ✅ Good - async DB operations
async def get_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return result.scalars().all()

# ✅ Good - async HTTP calls
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

## Pydantic v2 Models

```python
from pydantic import BaseModel, ConfigDict, Field

class UserCreate(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)
    username: str | None = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str | None
    
    # Pydantic v2 ORM mode
    model_config = ConfigDict(from_attributes=True)
```

## Schema Naming

| Suffix | Purpose | Example |
|--------|---------|---------|
| `*Create` | POST request body | `UserCreate` |
| `*Update` | PUT/PATCH request body | `UserUpdate` |
| `*Response` | API response | `UserResponse` |
| `*Input` | Internal service input | `CreateUserInput` |

## Import Order (PEP8)

```python
# 1. Standard library
import os
from datetime import datetime
from typing import Any

# 2. Third-party
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

# 3. Local imports
from app.config import settings
from app.models import User
from app.services.auth import AuthService
```

## String Formatting

```python
# ✅ Good - f-strings
message = f"Hello, {name}! You have {count} messages."

# ❌ Bad - concatenation or .format()
message = "Hello, " + name + "! You have " + str(count) + " messages."
message = "Hello, {}! You have {} messages.".format(name, count)
```

## Error Handling

```python
from app.core.exceptions import NotFoundError, InvalidCredentialsError

# In services - raise custom exceptions
async def get_user_or_404(db: AsyncSession, user_id: int) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user

# In routes - let exception handlers convert to HTTP responses
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_user_or_404(db, user_id)
```

## Function Size

Keep functions small (< 20 lines ideally). Extract helper functions.

```python
# ✅ Good - small, focused functions
async def create_user(db: AsyncSession, data: UserCreate) -> User:
    hashed_password = hash_password(data.password)
    user = User(email=data.email, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# ❌ Bad - doing too many things in one function
async def create_user_and_send_email_and_log_and_notify(...):
    ...
```

## Constants

Use UPPER_CASE for constants:

```python
# ✅ Good
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30
TOKEN_EXPIRY_MINUTES = 30

# ❌ Bad - magic numbers
if retry < 3:
    ...
```
