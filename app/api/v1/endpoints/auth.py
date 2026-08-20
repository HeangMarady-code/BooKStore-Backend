from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


def _get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower()).first()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)) -> User:
    """Register a new user account."""
    existing = _get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # The first registered user becomes the admin (superuser)
    is_first_user = db.query(User).count() == 0

    user = User(
        full_name=user_data.full_name,
        email=user_data.email.lower(),
        hashed_password=hash_password(user_data.password),
        is_superuser=is_first_user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """Login with username (email) and password to receive an access token."""
    user = _get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    token = create_access_token(subject=user.id)
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    """Get the profile of the currently authenticated user."""
    return current_user