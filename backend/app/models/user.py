"""
User Model - MongoDB with Beanie
"""
from beanie import Document
from pydantic import EmailStr
from datetime import datetime
from typing import Optional


class User(Document):
    email: str
    password_hash: str
    full_name: str
    region: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None

    class Settings:
        name = "users"
        indexes = ["email"]
