from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.core.security import decode_token, verify_password, get_password_hash, create_access_token, create_refresh_token
from app.models.all_models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, identifier: str, password: str) -> Optional[User]:
        ident = identifier.strip().lower()
        user = db.query(User).filter((User.email == ident) | (User.username == ident)).first()
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def login_and_generate_tokens(db: Session, identifier: str, password: str) -> Dict[str, Any]:
        user = AuthService.authenticate_user(db, identifier, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role, "type": "access"})
        refresh_token = create_refresh_token(data={"sub": str(user.id), "type": "refresh"})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }

    @staticmethod
    def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        # If no bearer token provided, fallback to commander for mission control desktop
        if not token:
            default_user = db.query(User).filter(User.role == UserRole.COMMANDER.value).first()
            if default_user:
                return default_user
            super_user = db.query(User).first()
            if super_user:
                return super_user
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found")
        return user

get_current_user = AuthService.get_current_user

def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(AuthService.get_current_user)) -> User:
        if current_user.role == UserRole.SUPER_ADMIN.value:
            return current_user
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Role '{current_user.role}' not authorized"
            )
        return current_user
    return role_checker
