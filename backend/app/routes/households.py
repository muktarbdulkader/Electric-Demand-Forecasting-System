"""
Household Management Routes - Ethiopian Electric Utility
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.request import (
    HouseholdCreate, HouseholdResponse, HouseholdAnalytics
)

router = APIRouter(prefix="/households", tags=["households"])

# In-memory storage (use database in production)
households_db = {}

# Ethiopian electricity tariff (Birr per kWh)
TARIFF_BIRR_PER_KWH = 2.75

def calculate_consumption(household: dict) -> float:
    """Calculate estimated monthly kWh consumption"""
    base = 50  # Base consumption per household
    per_person = 30  # kWh per person
    per_room = 20  # kWh per room
    ac_usage = 150 if household.get("has_ac") else 0
    heater_usage = 100 if household.get("has_heater") else 0
    ev_usage = 200 if household.get("has_ev") else 0
    appliances_usage = len(household.get("appliances", [])) * 15
    
    total = (
        base +
        (household["num_people"] * per_person) +
        (household["num_rooms"] * per_room) +
        ac_usage + heater_usage + ev_usage + appliances_usage
    )
    return round(total, 2)

@router.post("/", response_model=HouseholdResponse)
async def create_household(household: HouseholdCreate):
    """Register a new household"""
    household_id = len(households_db) + 1
    
    household_data = {
        "id": household_id,
        **household.dict()
    }
    
    estimated_kwh = calculate_consumption(household_data)
    household_data["estimated_monthly_kwh"] = estimated_kwh
    household_data["estimated_monthly_cost"] = round(estimated_kwh * TARIFF_BIRR_PER_KWH, 2)
    
    households_db[household_id] = household_data
    
    return HouseholdResponse(**household_data)

@router.get("/", response_model=List[HouseholdResponse])
async def list_households():
    """List all households"""
    return [HouseholdResponse(**h) for h in households_db.values()]

@router.get("/{household_id}", response_model=HouseholdResponse)
async def get_household(household_id: int):
    """Get household by ID"""
    if household_id not in households_db:
        raise HTTPException(status_code=404, detail="Household not found")
    return HouseholdResponse(**households_db[household_id])

@router.get("/analytics/summary", response_model=HouseholdAnalytics)
async def get_household_analytics():
    """Get household analytics summary"""
    if not households_db:
        # Return sample data if no households registered
        return HouseholdAnalytics(
            total_households=125000,
            total_population=625000,
            avg_consumption_kwh=180.5,
            peak_demand_mw=4850.0,
            regions={
                "Addis Ababa": {"households": 50000, "population": 250000},
                "Oromia": {"households": 30000, "population": 150000},
                "Amhara": {"households": 25000, "population": 125000},
                "Tigray": {"households": 10000, "population": 50000},
                "SNNPR": {"households": 10000, "population": 50000}
            }
        )
    
    total_households = len(households_db)
    total_population = sum(h["num_people"] for h in households_db.values())
    avg_consumption = sum(h["estimated_monthly_kwh"] for h in households_db.values()) / total_households
    
    # Group by region
    regions = {}
    for h in households_db.values():
        region = h["region"]
        if region not in regions:
            regions[region] = {"households": 0, "population": 0}
        regions[region]["households"] += 1
        regions[region]["population"] += h["num_people"]
    
    return HouseholdAnalytics(
        total_households=total_households,
        total_population=total_population,
        avg_consumption_kwh=round(avg_consumption, 2),
        peak_demand_mw=round(total_population * 0.008, 2),  # ~8W per person peak
        regions=regions
    )
