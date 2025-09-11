import os
from datetime import datetime, timedelta, timezone
from typing import Optional
# THE FIX: We need the `Request` object to read cookies
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import crud, models
from app.config import settings
from app.database import get_db

# --- Security Configuration ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        expire = datetime.now(timezone.utc) + timedelta(days=1)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# --- THE FIX: A more robust dependency that checks for a cookie ---
async def get_current_partner(request: Request, db: Session = Depends(get_db)) -> models.Partner:
    """
    A dependency that gets the current partner from a JWT token.
    It checks for the token in a secure, http-only cookie.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        detail="Not authenticated",
        headers={"Location": "/dashboard/login"},
    )
    
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception

    # The token in the cookie includes the "Bearer " prefix, so we need to remove it.
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

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

