from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Use pbkdf2_sha256 (no external bcrypt dependency).
# Avoids the known passlib 1.7.4 + bcrypt 5.x "__about__" incompatibility
# and supports passwords longer than 72 bytes.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)