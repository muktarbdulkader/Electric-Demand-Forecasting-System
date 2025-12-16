"""
Authentication Routes - Ethiopian Electric Utility
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import hashlib
import secrets

from app.schemas.request import (
    UserRegister, UserLogin, UserResponse, TokenResponse
)
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

# In-memory token storage (use Redis in production)
tokens_db = {}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    return secrets.token_urlsafe(32)


@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """Register a new user"""
    existing = await User.find_one(User.email == user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        full_name=user.full_name,
        region=user.region
    )
    await db_user.insert()
    
    token = generate_token()
    tokens_db[token] = str(db_user.id)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=str(db_user.id),
            email=db_user.email,
            full_name=db_user.full_name,
            region=db_user.region,
            created_at=db_user.created_at
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user"""
    user = await User.find_one(User.email == credentials.email)
    if not user or user.password_hash != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = generate_token()
    tokens_db[token] = str(user.id)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            region=user.region,
            created_at=user.created_at
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str):
    """Get current user info"""
    user_id = tokens_db.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        region=user.region,
        created_at=user.created_at
    )


@router.post("/logout")
async def logout(token: str):
    """Logout user"""
    if token in tokens_db:
        del tokens_db[token]
    return {"message": "Logged out successfully"}
