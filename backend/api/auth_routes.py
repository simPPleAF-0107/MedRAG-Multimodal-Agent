from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any
from pydantic import BaseModel

from backend.database.db import get_db
from backend.database.models import User, Patient
from backend.database import crud, schemas
from backend.core.security import verify_password, create_access_token
from backend.api.deps import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "doctor"

@router.post("/login")
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, getting an access token for future requests.
    """
    query = select(User).where(User.username == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
        
    sex = None
    if user.role == "patient":
        patient_query = select(Patient).where(Patient.user_account_id == user.id)
        patient_result = await db.execute(patient_query)
        patient = patient_result.scalars().first()
        if patient:
            sex = patient.sex

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "specialty": user.specialty,
        "sex": sex
    }

@router.post("/register")
async def register_user(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new user (doctor or patient).
    """
    # Check duplicate username
    existing = await crud.get_user_by_username(db, payload.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check duplicate email
    existing_email = await crud.get_user_by_email(db, payload.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_data = schemas.UserCreate(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        role=payload.role
    )
    
    new_user = await crud.create_user(db, user_data)
    
    return {
        "status": "success",
        "access_token": create_access_token(new_user.id),
        "token_type": "bearer",
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }

@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Return the current authenticated user's profile.
    """
    sex = None
    if current_user.role == "patient":
        patient_query = select(Patient).where(Patient.user_account_id == current_user.id)
        patient_result = await db.execute(patient_query)
        patient = patient_result.scalars().first()
        if patient:
            sex = patient.sex

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "specialty": current_user.specialty,
        "sex": sex
    }
