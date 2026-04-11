from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from backend.database.db import get_db
from backend.config import settings
from backend.database.models import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = payload.get("sub")
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    query = select(User).where(User.id == int(token_data))
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_doctor(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != "doctor" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough privileges, resource limited to Doctors.")
    return current_user


async def get_current_patient(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Not enough privileges, resource limited to Patients.")
    return current_user


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Soft-auth dependency: returns the authenticated User if a valid real JWT is present,
    returns None if no token or a demo placeholder token ('demo-bypass') is used.

    This allows pipeline endpoints to work in offline/demo mode (mock-auth sessions)
    without raising 401 and triggering the frontend's silent-logout interceptor.
    """
    auth_header = request.headers.get("Authorization", "")
    scheme, token = get_authorization_scheme_param(auth_header)

    if not token or scheme.lower() != "bearer":
        return None

    # Recognise offline demo placeholder — skip JWT validation
    if token == "demo-bypass":
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = payload.get("sub")
        if not token_data:
            return None
        query = select(User).where(User.id == int(token_data))
        result = await db.execute(query)
        return result.scalars().first()
    except Exception:
        return None
