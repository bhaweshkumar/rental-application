from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.providers import PasswordProvider
from app.database import get_db
from app.models.db.auth_provider import AuthProvider, ProviderType
from app.models.db.refresh_token import RefreshToken
from app.models.db.user import User
from app.models.schemas.auth import (
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserRead,
)
from app.models.schemas.envelope import ResponseEnvelope
from app.repositories.refresh_token_repo import refresh_token_repo
from app.repositories.user_repo import user_repo

router = APIRouter(prefix="/auth", tags=["auth"])

password_provider = PasswordProvider()


def _to_datetime(value: int | float) -> datetime:
    return datetime.utcfromtimestamp(int(value))


def _envelope(data: object) -> dict:
    return {"success": True, "data": data, "error": None}


@router.post("/register", response_model=ResponseEnvelope[Token])
def register(user_create: UserCreate, db: Session = Depends(get_db)) -> dict:
    existing = user_repo.get_by_email(db, email=user_create.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user = User(
        email=user_create.email,
        display_name=user_create.display_name,
    )
    user = user_repo.create(db, obj=user)

    hashed_password = password_provider.hash_credential(user_create.password)
    auth_provider = AuthProvider(
        user_id=user.id,
        provider=ProviderType.password,
        provider_user_id=user.email,
        hashed_credential=hashed_password,
    )
    db.add(auth_provider)
    db.commit()

    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)
    refresh_token_repo.create(
        db,
        obj=RefreshToken(
            user_id=user.id,
            token_hash=RefreshToken.hash_token(refresh_token),
            expires_at=_to_datetime(decode_token(refresh_token)["exp"]),
        ),
    )
    return _envelope(Token(access_token=access_token, refresh_token=refresh_token))


@router.post("/login", response_model=ResponseEnvelope[Token])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    user = user_repo.get_active_by_email(db, email=form_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_provider = db.exec(
        select(AuthProvider)
        .where(
            AuthProvider.user_id == user.id,
            AuthProvider.provider == ProviderType.password,
        )
    ).first()
    if auth_provider is None or auth_provider.hashed_credential is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not password_provider.verify_credential(form_data.password, auth_provider.hashed_credential):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)
    refresh_token_repo.create(
        db,
        obj=RefreshToken(
            user_id=user.id,
            token_hash=RefreshToken.hash_token(refresh_token),
            expires_at=_to_datetime(decode_token(refresh_token)["exp"]),
        ),
    )
    return _envelope(Token(access_token=access_token, refresh_token=refresh_token))


@router.post("/refresh", response_model=ResponseEnvelope[Token])
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)) -> dict:
    payload = decode_token(request.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_hash = RefreshToken.hash_token(request.refresh_token)
    existing = refresh_token_repo.get_by_hash(db, token_hash=token_hash)
    if existing is None or existing.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked or is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = str(payload["sub"])
    access_token = create_access_token(user_id=user_id)
    new_refresh_token = create_refresh_token(user_id=user_id)
    refresh_token_repo.revoke(db, db_obj=existing)
    refresh_token_repo.create(
        db,
        obj=RefreshToken(
            user_id=user_id,
            token_hash=RefreshToken.hash_token(new_refresh_token),
            expires_at=_to_datetime(decode_token(new_refresh_token)["exp"]),
        ),
    )
    return _envelope(Token(access_token=access_token, refresh_token=new_refresh_token))


@router.post("/logout", response_model=ResponseEnvelope[dict])
def logout(request: RefreshTokenRequest, db: Session = Depends(get_db)) -> dict:
    payload = decode_token(request.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_hash = RefreshToken.hash_token(request.refresh_token)
    existing = refresh_token_repo.get_by_hash(db, token_hash=token_hash)
    if existing is not None:
        refresh_token_repo.revoke(db, db_obj=existing)
    return _envelope({"success": True})


@router.get("/me", response_model=ResponseEnvelope[UserRead])
def read_users_me(current_user: User = Depends(get_current_user)) -> dict:
    return _envelope(current_user)
