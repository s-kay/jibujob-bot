import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import crud, models
from app.config import settings
from app.database import get_db

# --- Security Configuration ---

# This handles password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This tells FastAPI where to look for the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/dashboard/login")

# --- Password Utilities ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if a plain text password matches a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Creates a secure hash from a plain text password."""
    return pwd_context.hash(password)

# --- JWT Token Utilities ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default token expiration: 1 day
        expire = datetime.now(timezone.utc) + timedelta(days=1)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# --- FastAPI Dependency for Current User ---

def get_current_partner(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Partner:
    """
    A dependency that can be used in path operations to get the current authenticated partner.
    It verifies the JWT token and fetches the partner from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    partner = crud.get_partner_by_username(db, username=username)
    if partner is None:
        raise credentials_exception
    
    if not partner.is_active:
        raise HTTPException(status_code=400, detail="Inactive partner")

    return partner
