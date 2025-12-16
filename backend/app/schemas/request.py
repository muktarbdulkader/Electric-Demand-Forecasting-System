"""
Pydantic schemas for Ethiopian Electric Utility API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# ============ AUTH SCHEMAS ============
class UserRegister(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="Password")
    full_name: str = Field(..., description="Full name")
    region: str = Field(default="Addis Ababa", description="Region in Ethiopia")

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    region: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ============ HOUSEHOLD SCHEMAS ============
class HouseholdCreate(BaseModel):
    name: str = Field(..., description="Household name")
    region: str = Field(..., description="Region")
    num_people: int = Field(..., ge=1, description="Number of people")
    num_rooms: int = Field(..., ge=1, description="Number of rooms")
    has_ac: bool = Field(default=False, description="Has air conditioning")
    has_heater: bool = Field(default=False, description="Has electric heater")
    has_ev: bool = Field(default=False, description="Has electric vehicle")
    appliances: List[str] = Field(default=[], description="List of appliances")

class HouseholdResponse(BaseModel):
    id: str
    name: str
    region: str
    num_people: int
    num_rooms: int
    has_ac: bool
    has_heater: bool
    has_ev: bool
    appliances: List[str]
    estimated_monthly_kwh: float
    estimated_monthly_cost: float

class HouseholdAnalytics(BaseModel):
    total_households: int
    total_population: int
    avg_consumption_kwh: float
    peak_demand_mw: float
    regions: Dict[str, Dict[str, int]]

# ============ FORECAST SCHEMAS ============
class ForecastRequest(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday)")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    num_households: Optional[int] = Field(default=None, description="Number of households")
    population: Optional[int] = Field(default=None, description="Population")

class ForecastResponse(BaseModel):
    forecasted_demand: float = Field(..., description="Predicted demand in MW")
    confidence: float = Field(default=0.85, description="Prediction confidence")
    timestamp: datetime = Field(default_factory=datetime.now)

class HourlyForecast(BaseModel):
    hour: int
    temperature: float
    predicted_demand: float
    confidence: float = 0.85

class Forecast24hResponse(BaseModel):
    forecasts: List[HourlyForecast]
    base_temperature: float
    total_energy_mwh: float = 0
    peak_hour: int = 0
    peak_demand: float = 0
    generated_at: datetime = Field(default_factory=datetime.now)

class WeeklyForecast(BaseModel):
    day: str
    date: str
    avg_demand: float
    peak_demand: float
    min_demand: float
    total_energy_mwh: float

class ForecastWeeklyResponse(BaseModel):
    forecasts: List[WeeklyForecast]
    total_weekly_mwh: float
    avg_daily_peak: float

# ============ ANALYTICS SCHEMAS ============
class AnalyticsResponse(BaseModel):
    avg_demand: float
    max_demand: float
    min_demand: float
    peak_hour: int
    low_hour: int
    total_energy_24h: float = 0
    estimated_cost_birr: float = 0

class RegionAnalytics(BaseModel):
    region: str
    households: int
    population: int
    avg_demand_mw: float
    peak_demand_mw: float

class NationalAnalytics(BaseModel):
    total_households: int
    total_population: int
    total_demand_mw: float
    regions: List[RegionAnalytics]
    ai_insights: List[str]

# ============ AI INSIGHTS ============
class AIInsight(BaseModel):
    category: str
    message: str
    severity: str
    recommendation: str

class AIAnalysisResponse(BaseModel):
    insights: List[AIInsight]
    demand_trend: str
    efficiency_score: float
    recommendations: List[str]

# ============ UPLOAD ============
class UploadResponse(BaseModel):
    message: str
    records_processed: int
