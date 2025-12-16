"""
Ethiopian Electric Utility - Demand Forecasting API
Full-stack ML-powered system with authentication and AI insights
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes.forecast import router as forecast_router
from app.routes.auth import router as auth_router
from app.routes.households import router as households_router
from app.routes.ai_insights import router as ai_router
from app.routes.realtime import router as realtime_router
from app.routes.chatbot import router as chatbot_router
from app.routes.alerts import router as alerts_router
from app.routes.reports import router as reports_router

app = FastAPI(
    title="Ethiopian Electric Utility - Demand Forecasting API",
    description="ML-powered API for predicting electricity demand with AI insights",
    version="2.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(forecast_router)
app.include_router(auth_router)
app.include_router(households_router)
app.include_router(ai_router)
app.include_router(realtime_router)
app.include_router(chatbot_router)
app.include_router(alerts_router)
app.include_router(reports_router)

@app.get("/")
async def root():
    return {
        "message": "🇪🇹 Ethiopian Electric Utility - Demand Forecasting API",
        "version": "2.0.0",
        "features": [
            "ML-powered demand forecasting",
            "User authentication",
            "Household management",
            "AI-powered insights",
            "Regional analytics"
        ],
        "endpoints": {
            "forecast": ["/forecast", "/forecast/24h", "/analytics"],
            "auth": ["/auth/register", "/auth/login", "/auth/me"],
            "households": ["/households", "/households/analytics/summary"],
            "ai": ["/ai/insights", "/ai/national", "/ai/predict/weekly"],
            "alerts": ["/alerts", "/alerts/summary", "/alerts/config"],
            "reports": ["/reports/daily", "/reports/weekly", "/reports/export/{format}"]
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "EEU Demand Forecasting",
        "version": "2.0.0"
    }
