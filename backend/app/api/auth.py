from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import UserLoginRequest, TokenResponse, UserResponse
from ..services.auth_service import AuthService, get_current_user
from ..models.all_models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate operator/analyst and obtain JWT access & refresh tokens."""
    ident = login_data.username or login_data.email
    if not ident:
        raise HTTPException(status_code=400, detail="Username or email is required")
    return AuthService.login_and_generate_tokens(db, ident, login_data.password)

@router.post("/token", response_model=TokenResponse)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Standard OAuth2 form login compatible with Swagger UI."""
    return AuthService.login_and_generate_tokens(db, form_data.username, form_data.password)

@router.get("/me", response_model=UserResponse)
def get_current_operator(current_user: User = Depends(get_current_user)):
    """Return currently authenticated operator profile and permissions."""
    return current_user
