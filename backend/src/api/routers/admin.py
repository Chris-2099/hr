from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src import models
from src.api.schemas import CreateUserRequest, UserOut
from src.core.database import get_db
from src.core.deps import CurrentUser, require_roles
from src.utils.auth import hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _to_user_out(user: models.User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.name,
        is_active=user.is_active,
        department_scope=[s.department_id for s in user.department_scopes],
    )


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(models.ROLE_ADMIN)),
):
    users = db.query(models.User).order_by(models.User.email).all()
    return [_to_user_out(u) for u in users]


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    body: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(models.ROLE_ADMIN)),
):
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, detail=f"A user with email '{body.email}' already exists")
    role = db.query(models.Role).filter(models.Role.name == body.role).first()
    if not role:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Unknown role '{body.role}'")

    user = models.User(
        email=body.email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role_id=role.id,
    )
    db.add(user)
    db.flush()  # assigns user.id before attaching department scopes
    for department_id in body.department_ids:
        db.add(models.UserDepartmentScope(user_id=user.id, department_id=department_id))
    db.commit()
    db.refresh(user)
    return _to_user_out(user)


@router.post("/users/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(models.ROLE_ADMIN)),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return _to_user_out(user)
