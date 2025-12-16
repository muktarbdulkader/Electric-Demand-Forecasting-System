"""
Alert Model - MongoDB with Beanie
"""
from beanie import Document
from datetime import datetime
from typing import Optional
from enum import Enum


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertType(str, Enum):
    PEAK_DEMAND = "peak_demand"
    LOW_DEMAND = "low_demand"
    GRID_INSTABILITY = "grid_instability"
    MAINTENANCE = "maintenance"
    WEATHER = "weather"
    ANOMALY = "anomaly"
    FORECAST = "forecast"


class Alert(Document):
    alert_id: str
    type: str
    severity: str
    title: str
    message: str
    recommendation: str = ""
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "alerts"
        indexes = ["alert_id", "severity", "type"]
