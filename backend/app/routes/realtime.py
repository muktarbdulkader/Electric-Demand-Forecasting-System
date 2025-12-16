"""
Real-time Grid Information - Ethiopian Electric Utility
Live grid status, current demand, and real-time monitoring
"""
from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import Dict, List
import random

router = APIRouter(prefix="/realtime", tags=["realtime"])

# Ethiopian Power Plants Data
POWER_PLANTS = {
    "GERD": {"type": "Hydro", "capacity_mw": 5150, "location": "Benishangul-Gumuz", "status": "operational"},
    "Gilgel Gibe III": {"type": "Hydro", "capacity_mw": 1870, "location": "SNNPR", "status": "operational"},
    "Gilgel Gibe II": {"type": "Hydro", "capacity_mw": 420, "location": "SNNPR", "status": "operational"},
    "Gilgel Gibe I": {"type": "Hydro", "capacity_mw": 184, "location": "SNNPR", "status": "operational"},
    "Tekeze": {"type": "Hydro", "capacity_mw": 300, "location": "Tigray", "status": "operational"},
    "Tana Beles": {"type": "Hydro", "capacity_mw": 460, "location": "Amhara", "status": "operational"},
    "Fincha-Amerti-Neshe": {"type": "Hydro", "capacity_mw": 134, "location": "Oromia", "status": "operational"},
    "Koka": {"type": "Hydro", "capacity_mw": 43, "location": "Oromia", "status": "operational"},
    "Awash II & III": {"type": "Hydro", "capacity_mw": 64, "location": "Afar", "status": "operational"},
    "Metahara Sugar": {"type": "Biomass", "capacity_mw": 100, "location": "Oromia", "status": "operational"},
    "Adama Wind I": {"type": "Wind", "capacity_mw": 51, "location": "Oromia", "status": "operational"},
    "Adama Wind II": {"type": "Wind", "capacity_mw": 153, "location": "Oromia", "status": "operational"},
    "Ashegoda Wind": {"type": "Wind", "capacity_mw": 120, "location": "Tigray", "status": "maintenance"},
}

# Regional substations
SUBSTATIONS = {
    "Addis Ababa": ["Kality", "Kotebe", "Megenagna", "Bole", "Akaki"],
    "Oromia": ["Adama", "Bishoftu", "Jimma", "Nekemte", "Shashemene"],
    "Amhara": ["Bahir Dar", "Gondar", "Dessie", "Debre Markos"],
    "Tigray": ["Mekelle", "Axum", "Adigrat"],
    "SNNPR": ["Hawassa", "Arba Minch", "Wolaita Sodo"],
}

def get_current_hour_factor() -> float:
    """Get demand factor based on current hour"""
    hour = datetime.now().hour
    factors = {
        0: 0.65, 1: 0.58, 2: 0.52, 3: 0.48, 4: 0.46, 5: 0.50,
        6: 0.62, 7: 0.78, 8: 0.92, 9: 1.02, 10: 1.08, 11: 1.12,
        12: 1.15, 13: 1.12, 14: 1.08, 15: 1.04, 16: 1.00, 17: 1.08,
        18: 1.18, 19: 1.28, 20: 1.22, 21: 1.10, 22: 0.92, 23: 0.78
    }
    return factors.get(hour, 1.0)

@router.get("/status")
async def get_grid_status():
    """Get current grid status and real-time information"""
    now = datetime.now()
    hour_factor = get_current_hour_factor()
    
    # Calculate current demand
    base_demand = 3680
    current_demand = base_demand * hour_factor
    
    # Add some realistic variation
    variation = random.uniform(-50, 50)
    current_demand += variation
    
    # Calculate generation
    total_capacity = sum(p["capacity_mw"] for p in POWER_PLANTS.values())
    operational_capacity = sum(
        p["capacity_mw"] for p in POWER_PLANTS.values() 
        if p["status"] == "operational"
    )
    
    # Current generation (slightly above demand)
    current_generation = current_demand * 1.02
    
    # Reserve margin
    reserve_margin = ((operational_capacity - current_demand) / operational_capacity) * 100
    
    # Grid frequency (should be ~50 Hz)
    frequency = 50.0 + random.uniform(-0.05, 0.05)
    
    # Voltage levels
    voltage_230kv = 230 + random.uniform(-2, 2)
    voltage_132kv = 132 + random.uniform(-1, 1)
    voltage_66kv = 66 + random.uniform(-0.5, 0.5)
    
    return {
        "timestamp": now.isoformat(),
        "grid_status": "normal" if reserve_margin > 15 else "stressed",
        "current_demand_mw": round(current_demand, 2),
        "current_generation_mw": round(current_generation, 2),
        "total_capacity_mw": total_capacity,
        "operational_capacity_mw": operational_capacity,
        "reserve_margin_percent": round(reserve_margin, 2),
        "frequency_hz": round(frequency, 3),
        "voltage_levels": {
            "230kV": round(voltage_230kv, 2),
            "132kV": round(voltage_132kv, 2),
            "66kV": round(voltage_66kv, 2)
        },
        "load_factor": round(hour_factor, 3),
        "peak_today_mw": round(base_demand * 1.28, 2),
        "min_today_mw": round(base_demand * 0.46, 2)
    }

@router.get("/power-plants")
async def get_power_plants():
    """Get all power plants status"""
    plants = []
    hour_factor = get_current_hour_factor()
    
    for name, data in POWER_PLANTS.items():
        # Calculate current output based on status and demand
        if data["status"] == "operational":
            if data["type"] == "Hydro":
                output_factor = 0.7 + (hour_factor - 0.5) * 0.4
            elif data["type"] == "Wind":
                output_factor = random.uniform(0.2, 0.6)
            else:
                output_factor = 0.8
            current_output = data["capacity_mw"] * output_factor
        else:
            current_output = 0
        
        plants.append({
            "name": name,
            "type": data["type"],
            "capacity_mw": data["capacity_mw"],
            "current_output_mw": round(current_output, 2),
            "utilization_percent": round((current_output / data["capacity_mw"]) * 100, 1) if data["capacity_mw"] > 0 else 0,
            "location": data["location"],
            "status": data["status"]
        })
    
    # Sort by capacity
    plants.sort(key=lambda x: x["capacity_mw"], reverse=True)
    
    total_output = sum(p["current_output_mw"] for p in plants)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "plants": plants,
        "total_output_mw": round(total_output, 2),
        "generation_mix": {
            "hydro_percent": round(sum(p["current_output_mw"] for p in plants if p["type"] == "Hydro") / total_output * 100, 1),
            "wind_percent": round(sum(p["current_output_mw"] for p in plants if p["type"] == "Wind") / total_output * 100, 1),
            "other_percent": round(sum(p["current_output_mw"] for p in plants if p["type"] not in ["Hydro", "Wind"]) / total_output * 100, 1)
        }
    }

@router.get("/regional")
async def get_regional_demand():
    """Get demand by region"""
    hour_factor = get_current_hour_factor()
    
    regions = {
        "Addis Ababa": {"base_demand": 1200, "population": 4200000, "households": 850000},
        "Oromia": {"base_demand": 800, "population": 6000000, "households": 1200000},
        "Amhara": {"base_demand": 500, "population": 4000000, "households": 800000},
        "Tigray": {"base_demand": 300, "population": 2000000, "households": 400000},
        "SNNPR": {"base_demand": 400, "population": 3000000, "households": 600000},
        "Somali": {"base_demand": 150, "population": 1500000, "households": 300000},
        "Afar": {"base_demand": 80, "population": 750000, "households": 150000},
        "Benishangul-Gumuz": {"base_demand": 60, "population": 500000, "households": 100000},
        "Gambela": {"base_demand": 40, "population": 400000, "households": 80000},
        "Harari": {"base_demand": 50, "population": 250000, "households": 50000},
        "Dire Dawa": {"base_demand": 100, "population": 500000, "households": 100000}
    }
    
    regional_data = []
    for region, data in regions.items():
        current_demand = data["base_demand"] * hour_factor
        regional_data.append({
            "region": region,
            "current_demand_mw": round(current_demand, 2),
            "peak_demand_mw": round(data["base_demand"] * 1.28, 2),
            "population": data["population"],
            "households": data["households"],
            "per_capita_kw": round((current_demand * 1000) / data["population"], 4),
            "substations": SUBSTATIONS.get(region, [])
        })
    
    # Sort by demand
    regional_data.sort(key=lambda x: x["current_demand_mw"], reverse=True)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "regions": regional_data,
        "total_demand_mw": round(sum(r["current_demand_mw"] for r in regional_data), 2)
    }

@router.get("/weather")
async def get_weather_impact():
    """Get current weather and its impact on demand"""
    now = datetime.now()
    hour = now.hour
    
    # Simulated Ethiopian weather (Addis Ababa typical)
    temp_pattern = [15, 14, 13, 12, 12, 13, 15, 18, 21, 23, 25, 26,
                    27, 27, 27, 26, 25, 23, 21, 19, 18, 17, 16, 15]
    
    current_temp = temp_pattern[hour] + random.uniform(-2, 2)
    humidity = 60 + random.uniform(-10, 10)
    
    # Weather impact on demand
    temp_impact = (current_temp - 22) * 15  # MW per degree from comfort zone
    humidity_impact = (humidity - 60) * 2 if humidity > 70 else 0
    
    return {
        "timestamp": now.isoformat(),
        "location": "Addis Ababa (Reference)",
        "temperature_c": round(current_temp, 1),
        "humidity_percent": round(humidity, 1),
        "conditions": "Clear" if humidity < 60 else "Partly Cloudy" if humidity < 75 else "Cloudy",
        "demand_impact": {
            "temperature_impact_mw": round(temp_impact, 2),
            "humidity_impact_mw": round(humidity_impact, 2),
            "total_impact_mw": round(temp_impact + humidity_impact, 2)
        },
        "forecast": {
            "next_6h_temp_avg": round(sum(temp_pattern[(hour + i) % 24] for i in range(6)) / 6, 1),
            "expected_peak_temp": max(temp_pattern),
            "expected_low_temp": min(temp_pattern)
        }
    }

@router.get("/alerts")
async def get_current_alerts():
    """Get current grid alerts and warnings"""
    now = datetime.now()
    hour = now.hour
    hour_factor = get_current_hour_factor()
    
    alerts = []
    
    # Peak hour alert
    if 18 <= hour <= 21:
        alerts.append({
            "id": 1,
            "type": "warning",
            "category": "Peak Demand",
            "message": "Currently in evening peak period (18:00-21:00)",
            "recommendation": "Industrial users should reduce non-essential loads",
            "timestamp": now.isoformat()
        })
    
    # High demand alert
    if hour_factor > 1.2:
        alerts.append({
            "id": 2,
            "type": "critical",
            "category": "High Demand",
            "message": f"Demand at {hour_factor*100:.0f}% of base load",
            "recommendation": "Activate all available generation capacity",
            "timestamp": now.isoformat()
        })
    
    # Maintenance notice
    alerts.append({
        "id": 3,
        "type": "info",
        "category": "Maintenance",
        "message": "Ashegoda Wind Farm under scheduled maintenance",
        "recommendation": "120 MW capacity temporarily unavailable",
        "timestamp": now.isoformat()
    })
    
    # Low demand opportunity
    if hour_factor < 0.6:
        alerts.append({
            "id": 4,
            "type": "info",
            "category": "Low Demand",
            "message": "Off-peak period - optimal for maintenance",
            "recommendation": "Schedule grid maintenance activities",
            "timestamp": now.isoformat()
        })
    
    return {
        "timestamp": now.isoformat(),
        "alerts": alerts,
        "alert_count": len(alerts),
        "critical_count": len([a for a in alerts if a["type"] == "critical"]),
        "warning_count": len([a for a in alerts if a["type"] == "warning"])
    }

@router.get("/summary")
async def get_realtime_summary():
    """Get comprehensive real-time summary"""
    now = datetime.now()
    hour_factor = get_current_hour_factor()
    base_demand = 3680
    current_demand = base_demand * hour_factor
    
    return {
        "timestamp": now.isoformat(),
        "current_time": now.strftime("%H:%M:%S"),
        "current_date": now.strftime("%Y-%m-%d"),
        "day_of_week": now.strftime("%A"),
        "demand": {
            "current_mw": round(current_demand, 2),
            "peak_today_mw": round(base_demand * 1.28, 2),
            "min_today_mw": round(base_demand * 0.46, 2),
            "avg_today_mw": round(base_demand * 0.95, 2)
        },
        "generation": {
            "total_capacity_mw": 9049,
            "available_mw": 8929,
            "current_output_mw": round(current_demand * 1.02, 2),
            "reserve_mw": round(8929 - current_demand, 2)
        },
        "grid_health": {
            "status": "normal",
            "frequency_hz": round(50.0 + random.uniform(-0.02, 0.02), 3),
            "stability": "stable"
        },
        "quick_stats": {
            "households_served": "4.6M",
            "population_served": "23M",
            "regions_connected": 11,
            "power_plants_online": 12
        }
    }
