"""
Alerts & Notifications System - Ethiopian Electric Utility
Email, SMS, and push notification alerts for grid events
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
from enum import Enum
import os

router = APIRouter(prefix="/alerts", tags=["alerts"])

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

class AlertConfig(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    email_recipients: List[str] = []
    sms_recipients: List[str] = []
    min_severity: AlertSeverity = AlertSeverity.WARNING

class Alert(BaseModel):
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    recommendation: str
    timestamp: str
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[str] = None

class CreateAlertRequest(BaseModel):
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    recommendation: str = ""

# In-memory alert storage (use database in production)
alerts_db: List[Alert] = []
alert_config = AlertConfig()
alert_subscriptions = {}

# Initialize with sample alerts for demonstration
def init_sample_alerts():
    """Add sample alerts on startup"""
    if len(alerts_db) == 0:
        sample_alerts = [
            Alert(
                id="ALT-20251216-0001",
                type=AlertType.PEAK_DEMAND,
                severity=AlertSeverity.WARNING,
                title="📈 WARNING: Elevated Evening Demand",
                message="Evening peak demand reached 4,200 MW at 19:00",
                recommendation="Monitor closely. Industrial users advised to reduce non-essential loads.",
                timestamp=datetime.now().replace(hour=19, minute=0).isoformat()
            ),
            Alert(
                id="ALT-20251216-0002",
                type=AlertType.MAINTENANCE,
                severity=AlertSeverity.INFO,
                title="🔧 Scheduled Maintenance: Ashegoda Wind Farm",
                message="Ashegoda Wind Farm (120 MW) under scheduled maintenance until Dec 18",
                recommendation="Capacity temporarily reduced. No action required.",
                timestamp=datetime.now().replace(hour=8, minute=0).isoformat()
            ),
            Alert(
                id="ALT-20251216-0003",
                type=AlertType.WEATHER,
                severity=AlertSeverity.INFO,
                title="🌡️ Weather Advisory: Temperature Drop Expected",
                message="Temperature expected to drop 5°C tonight, may increase heating demand",
                recommendation="Prepare additional generation capacity for morning peak.",
                timestamp=datetime.now().replace(hour=14, minute=30).isoformat()
            ),
        ]
        alerts_db.extend(sample_alerts)

# Initialize sample alerts
init_sample_alerts()

def generate_alert_id() -> str:
    """Generate unique alert ID"""
    return f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(alerts_db)+1:04d}"

def check_thresholds(demand_mw: float, capacity_mw: float = 9000) -> List[Alert]:
    """Check demand against thresholds and generate alerts"""
    alerts = []
    utilization = (demand_mw / capacity_mw) * 100
    
    if utilization > 95:
        alerts.append(Alert(
            id=generate_alert_id(),
            type=AlertType.PEAK_DEMAND,
            severity=AlertSeverity.EMERGENCY,
            title="🚨 EMERGENCY: Grid at Critical Capacity",
            message=f"Current demand ({demand_mw:.0f} MW) is at {utilization:.1f}% of capacity",
            recommendation="Implement immediate load shedding. Activate all emergency reserves.",
            timestamp=datetime.now().isoformat()
        ))
    elif utilization > 85:
        alerts.append(Alert(
            id=generate_alert_id(),
            type=AlertType.PEAK_DEMAND,
            severity=AlertSeverity.CRITICAL,
            title="⚠️ CRITICAL: High Grid Utilization",
            message=f"Current demand ({demand_mw:.0f} MW) is at {utilization:.1f}% of capacity",
            recommendation="Prepare load shedding protocols. Alert major industrial consumers.",
            timestamp=datetime.now().isoformat()
        ))
    elif utilization > 75:
        alerts.append(Alert(
            id=generate_alert_id(),
            type=AlertType.PEAK_DEMAND,
            severity=AlertSeverity.WARNING,
            title="📈 WARNING: Elevated Demand",
            message=f"Current demand ({demand_mw:.0f} MW) is at {utilization:.1f}% of capacity",
            recommendation="Monitor closely. Prepare backup generation capacity.",
            timestamp=datetime.now().isoformat()
        ))
    
    return alerts

async def send_email_alert(alert: Alert, recipients: List[str]):
    """Send email alert (placeholder - integrate with SMTP)"""
    # In production, use smtplib or email service like SendGrid
    print(f"📧 Email alert sent to {recipients}: {alert.title}")

async def send_sms_alert(alert: Alert, recipients: List[str]):
    """Send SMS alert (placeholder - integrate with SMS gateway)"""
    # In production, use Twilio or local SMS gateway
    print(f"📱 SMS alert sent to {recipients}: {alert.title}")

async def send_push_notification(alert: Alert):
    """Send push notification (placeholder)"""
    print(f"🔔 Push notification: {alert.title}")

@router.get("/")
async def get_alerts(
    severity: Optional[AlertSeverity] = None,
    alert_type: Optional[AlertType] = None,
    acknowledged: Optional[bool] = None,
    limit: int = 50
):
    """Get all alerts with optional filtering"""
    filtered = alerts_db.copy()
    
    if severity:
        filtered = [a for a in filtered if a.severity == severity]
    if alert_type:
        filtered = [a for a in filtered if a.type == alert_type]
    if acknowledged is not None:
        filtered = [a for a in filtered if a.acknowledged == acknowledged]
    
    # Sort by timestamp descending
    filtered.sort(key=lambda x: x.timestamp, reverse=True)
    
    return {
        "alerts": filtered[:limit],
        "total": len(filtered),
        "unacknowledged": len([a for a in alerts_db if not a.acknowledged])
    }

@router.post("/create")
async def create_alert(request: CreateAlertRequest, background_tasks: BackgroundTasks):
    """Create a new alert"""
    alert = Alert(
        id=generate_alert_id(),
        type=request.type,
        severity=request.severity,
        title=request.title,
        message=request.message,
        recommendation=request.recommendation,
        timestamp=datetime.now().isoformat()
    )
    
    alerts_db.append(alert)
    
    # Send notifications based on config
    if alert_config.email_enabled and alert_config.email_recipients:
        background_tasks.add_task(send_email_alert, alert, alert_config.email_recipients)
    if alert_config.sms_enabled and alert_config.sms_recipients:
        background_tasks.add_task(send_sms_alert, alert, alert_config.sms_recipients)
    if alert_config.push_enabled:
        background_tasks.add_task(send_push_notification, alert)
    
    return {"message": "Alert created", "alert": alert}

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, user: str = "operator"):
    """Acknowledge an alert"""
    for alert in alerts_db:
        if alert.id == alert_id:
            alert.acknowledged = True
            alert.acknowledged_by = user
            alert.acknowledged_at = datetime.now().isoformat()
            return {"message": "Alert acknowledged", "alert": alert}
    
    raise HTTPException(status_code=404, detail="Alert not found")

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete an alert"""
    global alerts_db
    alerts_db = [a for a in alerts_db if a.id != alert_id]
    return {"message": "Alert deleted"}

@router.get("/config")
async def get_alert_config():
    """Get alert configuration"""
    return alert_config

@router.put("/config")
async def update_alert_config(config: AlertConfig):
    """Update alert configuration"""
    global alert_config
    alert_config = config
    return {"message": "Configuration updated", "config": alert_config}

@router.get("/thresholds")
async def get_alert_thresholds():
    """Get alert threshold settings"""
    return {
        "thresholds": {
            "emergency": {"utilization_percent": 95, "description": "Grid at critical capacity"},
            "critical": {"utilization_percent": 85, "description": "High grid utilization"},
            "warning": {"utilization_percent": 75, "description": "Elevated demand"},
            "info": {"utilization_percent": 50, "description": "Normal operation"}
        },
        "capacity_mw": 9000,
        "current_settings": {
            "email_enabled": alert_config.email_enabled,
            "sms_enabled": alert_config.sms_enabled,
            "min_severity": alert_config.min_severity
        }
    }

@router.post("/check-demand")
async def check_demand_alerts(demand_mw: float, background_tasks: BackgroundTasks):
    """Check current demand and generate alerts if needed"""
    new_alerts = check_thresholds(demand_mw)
    
    for alert in new_alerts:
        alerts_db.append(alert)
        if alert_config.push_enabled:
            background_tasks.add_task(send_push_notification, alert)
    
    return {
        "demand_mw": demand_mw,
        "alerts_generated": len(new_alerts),
        "alerts": new_alerts
    }

@router.get("/summary")
async def get_alerts_summary():
    """Get alerts summary for dashboard"""
    now = datetime.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    recent_24h = [a for a in alerts_db if datetime.fromisoformat(a.timestamp) > last_24h]
    recent_7d = [a for a in alerts_db if datetime.fromisoformat(a.timestamp) > last_7d]
    
    return {
        "total_alerts": len(alerts_db),
        "unacknowledged": len([a for a in alerts_db if not a.acknowledged]),
        "last_24h": {
            "total": len(recent_24h),
            "emergency": len([a for a in recent_24h if a.severity == AlertSeverity.EMERGENCY]),
            "critical": len([a for a in recent_24h if a.severity == AlertSeverity.CRITICAL]),
            "warning": len([a for a in recent_24h if a.severity == AlertSeverity.WARNING])
        },
        "last_7d": {
            "total": len(recent_7d),
            "by_type": {
                t.value: len([a for a in recent_7d if a.type == t])
                for t in AlertType
            }
        },
        "latest_alert": alerts_db[-1] if alerts_db else None
    }

@router.post("/subscribe")
async def subscribe_to_alerts(email: str, alert_types: List[AlertType] = None):
    """Subscribe to alert notifications"""
    alert_subscriptions[email] = {
        "email": email,
        "types": alert_types or list(AlertType),
        "subscribed_at": datetime.now().isoformat()
    }
    return {"message": f"Subscribed {email} to alerts"}

@router.delete("/subscribe/{email}")
async def unsubscribe_from_alerts(email: str):
    """Unsubscribe from alerts"""
    if email in alert_subscriptions:
        del alert_subscriptions[email]
        return {"message": f"Unsubscribed {email}"}
    raise HTTPException(status_code=404, detail="Subscription not found")
