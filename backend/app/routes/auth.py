"""
Authentication Routes - Ethiopian Electric Utility
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import hashlib
import secrets

from app.schemas.request import (
    UserRegister, UserLogin, UserResponse, TokenResponse
)

router = APIRouter(prefix="/auth", tags=["authentication"])

# In-memory user storage (use database in production)
users_db = {}
tokens_db = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_urlsafe(32)

@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """Register a new user"""
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = len(users_db) + 1
    user_data = {
        "id": user_id,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "full_name": user.full_name,
        "region": user.region,
        "created_at": datetime.now()
    }
    users_db[user.email] = user_data
    
    token = generate_token()
    tokens_db[token] = user.email
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_data["id"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            region=user_data["region"],
            created_at=user_data["created_at"]
        )
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user"""
    user = users_db.get(credentials.email)
    if not user or user["password_hash"] != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = generate_token()
    tokens_db[token] = credentials.email
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            region=user["region"],
            created_at=user["created_at"]
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str):
    """Get current user info"""
    email = tokens_db.get(token)
    if not email or email not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = users_db[email]
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        region=user["region"],
        created_at=user["created_at"]
    )

@router.post("/logout")
async def logout(token: str):
    """Logout user"""
    if token in tokens_db:
        del tokens_db[token]
    return {"message": "Logged out successfully"}
