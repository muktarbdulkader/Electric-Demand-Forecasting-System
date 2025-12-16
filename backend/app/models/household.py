"""
Household Model - MongoDB with Beanie
"""
from beanie import Document
from datetime import datetime
from typing import Optional, List


class Household(Document):
    name: str
    region: str
    num_people: int = 1
    num_rooms: int = 1
    has_ac: bool = False
    has_heater: bool = False
    has_ev: bool = False
    appliances: List[str] = []
    estimated_monthly_kwh: float = 0.0
    estimated_monthly_cost: float = 0.0
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None

    class Settings:
        name = "households"
        indexes = ["region"]
