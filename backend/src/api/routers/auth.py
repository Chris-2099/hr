from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src import models
from src.api.schemas import LoginRequest, MeResponse, TokenResponse
from src.core.database import get_db
from src.core.deps import CurrentUser, get_current_user
from src.utils.auth import create_access_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")
    token = create_access_token(subject=user.email, extra_claims={"role": user.role.name})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(current_user: CurrentUser = Depends(get_current_user)):
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        can_view_compensation=current_user.can_view_compensation,
        department_scope=current_user.department_ids,
    )
