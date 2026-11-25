from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src import models
from src.core.config import settings
from src.core.database import get_db
from src.utils.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


class CurrentUser:
    """Resolved identity + access scope for the request, computed once."""

    def __init__(self, user: models.User):
        self.id = user.id
        self.email = user.email
        self.full_name = user.full_name
        self.role: str = user.role.name
        self.employee_id = user.employee_id
        self.can_view_compensation: bool = models.ROLE_COMP_VISIBILITY.get(self.role, False)
        self.department_ids: list[str] | None = None  # None == unrestricted (all departments)
        if self.role == models.ROLE_HRBP:
            self.department_ids = [s.department_id for s in user.department_scopes]


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    x_dev_user_email: str | None = Header(default=None),
) -> CurrentUser:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if settings.DISABLE_AUTH:
        # DEV ONLY - see config.py. No token required; optionally
        # impersonate any seeded user via X-Dev-User-Email to exercise RBAC
        # without logging in.
        email = x_dev_user_email or settings.DEV_DEFAULT_USER_EMAIL
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"DISABLE_AUTH is on but dev user '{email}' was not found. Re-run the seed script.",
            )
        return CurrentUser(user)

    if not token:
        raise credentials_error
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise credentials_error
    user = db.query(models.User).filter(models.User.email == payload["sub"]).first()
    if not user or not user.is_active:
        raise credentials_error
    return CurrentUser(user)


def require_roles(*allowed_roles: str):
    def _check(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not permitted to access this resource",
            )
        return current_user

    return _check


def department_filter_ids(current_user: CurrentUser, all_department_ids: list[str]) -> list[str]:
    """Returns the department_ids this user may see. None scope => all."""
    if current_user.department_ids is None:
        return all_department_ids
    return current_user.department_ids
