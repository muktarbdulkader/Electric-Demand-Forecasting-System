"""
External Data Integration - Ethiopian Electric Utility Platform
Weather APIs, EEU data import, and future API integration structure
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import httpx
import os
import json

router = APIRouter(prefix="/external", tags=["external-data"])

# Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
WEATHER_CACHE_MINUTES = 30

# Ethiopian cities coordinates
ETHIOPIAN_CITIES = {
    "Addis Ababa": {"lat": 9.0320, "lon": 38.7469, "region": "Addis Ababa"},
    "Dire Dawa": {"lat": 9.6009, "lon": 41.8501, "region": "Dire Dawa"},
    "Mekelle": {"lat": 13.4967, "lon": 39.4753, "region": "Tigray"},
    "Gondar": {"lat": 12.6030, "lon": 37.4521, "region": "Amhara"},
    "Bahir Dar": {"lat": 11.5742, "lon": 37.3614, "region": "Amhara"},
    "Hawassa": {"lat": 7.0504, "lon": 38.4955, "region": "SNNPR"},
    "Adama": {"lat": 8.5400, "lon": 39.2700, "region": "Oromia"},
    "Jimma": {"lat": 7.6667, "lon": 36.8333, "region": "Oromia"},
    "Dessie": {"lat": 11.1333, "lon": 39.6333, "region": "Amhara"},
    "Jijiga": {"lat": 9.3500, "lon": 42.8000, "region": "Somali"},
}

# Weather cache
_weather_cache: Dict[str, Any] = {}
_cache_timestamp: Optional[datetime] = None


class WeatherData(BaseModel):
    city: str
    temperature_c: float
    feels_like_c: float
    humidity_percent: float
    pressure_hpa: float
    wind_speed_ms: float
    description: str
    icon: str
    timestamp: str


class EEUDataSource(str, Enum):
    ANNUAL_REPORT = "annual_report"
    MONTHLY_STATS = "monthly_stats"
    REGIONAL_DATA = "regional_data"
    GENERATION_MIX = "generation_mix"


class EEUImportRequest(BaseModel):
    source_type: EEUDataSource
    year: int
    data: Dict[str, Any]


# ============== WEATHER API INTEGRATION ==============

@router.get("/weather/current/{city}")
async def get_current_weather(city: str):
    """Get current weather for Ethiopian city using OpenWeatherMap API"""
    if city not in ETHIOPIAN_CITIES:
        raise HTTPException(
            status_code=404, 
            detail=f"City not found. Available: {list(ETHIOPIAN_CITIES.keys())}"
        )
    
    city_data = ETHIOPIAN_CITIES[city]
    
    # Check cache first
    cache_key = f"weather_{city}"
    if cache_key in _weather_cache:
        cached = _weather_cache[cache_key]
        cache_age = (datetime.now() - cached["timestamp"]).total_seconds() / 60
        if cache_age < WEATHER_CACHE_MINUTES:
            return cached["data"]
    
    # If no API key, return simulated data
    if not OPENWEATHER_API_KEY:
        return get_simulated_weather(city, city_data)
    
    # Fetch from OpenWeatherMap
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": city_data["lat"],
                    "lon": city_data["lon"],
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                weather = {
                    "city": city,
                    "region": city_data["region"],
                    "coordinates": {"lat": city_data["lat"], "lon": city_data["lon"]},
                    "temperature_c": round(data["main"]["temp"], 1),
                    "feels_like_c": round(data["main"]["feels_like"], 1),
                    "humidity_percent": data["main"]["humidity"],
                    "pressure_hpa": data["main"]["pressure"],
                    "wind_speed_ms": data["wind"]["speed"],
                    "description": data["weather"][0]["description"],
                    "icon": data["weather"][0]["icon"],
                    "timestamp": datetime.now().isoformat(),
                    "source": "openweathermap"
                }
                
                # Cache the result
                _weather_cache[cache_key] = {
                    "data": weather,
                    "timestamp": datetime.now()
                }
                
                return weather
            else:
                return get_simulated_weather(city, city_data)
                
    except Exception as e:
        print(f"Weather API error: {e}")
        return get_simulated_weather(city, city_data)


def get_simulated_weather(city: str, city_data: dict) -> dict:
    """Generate realistic simulated weather for Ethiopian cities"""
    import random
    hour = datetime.now().hour
    
    # Base temperatures vary by altitude/region
    base_temps = {
        "Addis Ababa": 18,  # Highland
        "Dire Dawa": 28,    # Lowland, hot
        "Mekelle": 20,      # Highland
        "Gondar": 19,       # Highland
        "Bahir Dar": 21,    # Lake region
        "Hawassa": 22,      # Lake region
        "Adama": 24,        # Rift valley
        "Jimma": 20,        # Highland
        "Dessie": 17,       # Highland
        "Jijiga": 26,       # Semi-arid
    }
    
    base_temp = base_temps.get(city, 22)
    
    # Daily temperature variation
    temp_variation = [-4, -5, -6, -6, -5, -4, -2, 0, 2, 4, 6, 8,
                      9, 10, 10, 9, 8, 6, 4, 2, 0, -1, -2, -3]
    
    current_temp = base_temp + temp_variation[hour] + random.uniform(-2, 2)
    
    return {
        "city": city,
        "region": city_data["region"],
        "coordinates": {"lat": city_data["lat"], "lon": city_data["lon"]},
        "temperature_c": round(current_temp, 1),
        "feels_like_c": round(current_temp - 1, 1),
        "humidity_percent": round(55 + random.uniform(-15, 15)),
        "pressure_hpa": round(1013 + random.uniform(-5, 5)),
        "wind_speed_ms": round(2 + random.uniform(0, 4), 1),
        "description": "partly cloudy" if random.random() > 0.5 else "clear sky",
        "icon": "02d" if hour < 18 else "02n",
        "timestamp": datetime.now().isoformat(),
        "source": "simulated"
    }


@router.get("/weather/all")
async def get_all_cities_weather():
    """Get weather for all major Ethiopian cities"""
    results = []
    for city in ETHIOPIAN_CITIES.keys():
        weather = await get_current_weather(city)
        results.append(weather)
    
    # Calculate national average
    avg_temp = sum(w["temperature_c"] for w in results) / len(results)
    avg_humidity = sum(w["humidity_percent"] for w in results) / len(results)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "cities": results,
        "national_average": {
            "temperature_c": round(avg_temp, 1),
            "humidity_percent": round(avg_humidity, 1)
        },
        "demand_impact": calculate_weather_demand_impact(avg_temp, avg_humidity)
    }


def calculate_weather_demand_impact(temp: float, humidity: float) -> dict:
    """Calculate how weather affects electricity demand"""
    # Comfort zone is 20-25°C
    if temp < 20:
        temp_impact = (20 - temp) * 25  # Heating demand
        impact_type = "heating"
    elif temp > 25:
        temp_impact = (temp - 25) * 35  # Cooling demand (AC uses more power)
        impact_type = "cooling"
    else:
        temp_impact = 0
        impact_type = "neutral"
    
    # High humidity increases AC usage
    humidity_impact = max(0, (humidity - 70) * 5) if temp > 25 else 0
    
    total_impact = temp_impact + humidity_impact
    
    return {
        "temperature_impact_mw": round(temp_impact, 1),
        "humidity_impact_mw": round(humidity_impact, 1),
        "total_impact_mw": round(total_impact, 1),
        "impact_type": impact_type,
        "description": f"Weather conditions {'increasing' if total_impact > 0 else 'not significantly affecting'} demand"
    }


@router.get("/weather/forecast/{city}")
async def get_weather_forecast(city: str, days: int = 3):
    """Get weather forecast for demand planning"""
    if city not in ETHIOPIAN_CITIES:
        raise HTTPException(status_code=404, detail="City not found")
    
    city_data = ETHIOPIAN_CITIES[city]
    
    # If API key available, fetch real forecast
    if OPENWEATHER_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openweathermap.org/data/2.5/forecast",
                    params={
                        "lat": city_data["lat"],
                        "lon": city_data["lon"],
                        "appid": OPENWEATHER_API_KEY,
                        "units": "metric",
                        "cnt": days * 8  # 3-hour intervals
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    forecasts = []
                    for item in data["list"]:
                        forecasts.append({
                            "datetime": item["dt_txt"],
                            "temperature_c": round(item["main"]["temp"], 1),
                            "humidity_percent": item["main"]["humidity"],
                            "description": item["weather"][0]["description"]
                        })
                    return {
                        "city": city,
                        "forecasts": forecasts,
                        "source": "openweathermap"
                    }
        except Exception as e:
            print(f"Forecast API error: {e}")
    
    # Return simulated forecast
    return generate_simulated_forecast(city, city_data, days)


def generate_simulated_forecast(city: str, city_data: dict, days: int) -> dict:
    """Generate simulated weather forecast"""
    import random
    
    base_temps = {
        "Addis Ababa": 18, "Dire Dawa": 28, "Mekelle": 20,
        "Gondar": 19, "Bahir Dar": 21, "Hawassa": 22,
        "Adama": 24, "Jimma": 20, "Dessie": 17, "Jijiga": 26,
    }
    
    base_temp = base_temps.get(city, 22)
    forecasts = []
    
    for day in range(days):
        for hour in [6, 12, 18, 0]:
            dt = datetime.now() + timedelta(days=day, hours=hour - datetime.now().hour)
            temp_var = [-3, 8, 5, -2][hour // 6]
            
            forecasts.append({
                "datetime": dt.strftime("%Y-%m-%d %H:00:00"),
                "temperature_c": round(base_temp + temp_var + random.uniform(-2, 2), 1),
                "humidity_percent": round(55 + random.uniform(-10, 10)),
                "description": random.choice(["clear sky", "partly cloudy", "scattered clouds"])
            })
    
    return {
        "city": city,
        "forecasts": forecasts,
        "source": "simulated"
    }


# ============== EEU DATA IMPORT ==============

# Historical EEU data (from annual reports)
EEU_HISTORICAL_DATA = {
    2023: {
        "total_capacity_mw": 5200,
        "peak_demand_mw": 4800,
        "generation_gwh": 15500,
        "customers": 4600000,
        "access_rate_percent": 55,
        "generation_mix": {
            "hydro": 90,
            "wind": 6,
            "thermal": 3,
            "solar": 1
        },
        "regional_demand_percent": {
            "Addis Ababa": 35,
            "Oromia": 22,
            "Amhara": 14,
            "SNNPR": 10,
            "Tigray": 8,
            "Others": 11
        }
    },
    2022: {
        "total_capacity_mw": 4500,
        "peak_demand_mw": 4200,
        "generation_gwh": 14200,
        "customers": 4200000,
        "access_rate_percent": 51,
        "generation_mix": {
            "hydro": 92,
            "wind": 5,
            "thermal": 2,
            "solar": 1
        }
    },
    2021: {
        "total_capacity_mw": 4300,
        "peak_demand_mw": 3900,
        "generation_gwh": 13100,
        "customers": 3800000,
        "access_rate_percent": 48
    }
}


@router.get("/eeu/historical")
async def get_eeu_historical_data(year: Optional[int] = None):
    """Get historical EEU statistics from annual reports"""
    if year:
        if year not in EEU_HISTORICAL_DATA:
            raise HTTPException(
                status_code=404,
                detail=f"Data not available for {year}. Available years: {list(EEU_HISTORICAL_DATA.keys())}"
            )
        return {
            "year": year,
            "data": EEU_HISTORICAL_DATA[year],
            "source": "EEU Annual Report"
        }
    
    return {
        "available_years": list(EEU_HISTORICAL_DATA.keys()),
        "data": EEU_HISTORICAL_DATA,
        "source": "EEU Annual Reports"
    }


@router.post("/eeu/import")
async def import_eeu_data(request: EEUImportRequest):
    """Import EEU data from annual reports or other sources"""
    
    # Validate and store the data
    if request.year in EEU_HISTORICAL_DATA:
        # Update existing year
        EEU_HISTORICAL_DATA[request.year].update(request.data)
        action = "updated"
    else:
        # Add new year
        EEU_HISTORICAL_DATA[request.year] = request.data
        action = "added"
    
    return {
        "message": f"EEU data for {request.year} {action} successfully",
        "source_type": request.source_type,
        "year": request.year,
        "fields_imported": list(request.data.keys())
    }


@router.get("/eeu/growth-analysis")
async def get_growth_analysis():
    """Analyze EEU growth trends for forecasting"""
    years = sorted(EEU_HISTORICAL_DATA.keys())
    
    if len(years) < 2:
        return {"message": "Need at least 2 years of data for analysis"}
    
    analysis = {
        "period": f"{years[0]}-{years[-1]}",
        "metrics": {}
    }
    
    # Calculate growth rates
    metrics = ["total_capacity_mw", "peak_demand_mw", "generation_gwh", "customers"]
    
    for metric in metrics:
        values = []
        for year in years:
            if metric in EEU_HISTORICAL_DATA[year]:
                values.append({
                    "year": year,
                    "value": EEU_HISTORICAL_DATA[year][metric]
                })
        
        if len(values) >= 2:
            first = values[0]["value"]
            last = values[-1]["value"]
            years_diff = values[-1]["year"] - values[0]["year"]
            
            total_growth = ((last - first) / first) * 100
            annual_growth = total_growth / years_diff if years_diff > 0 else 0
            
            analysis["metrics"][metric] = {
                "values": values,
                "total_growth_percent": round(total_growth, 2),
                "annual_growth_percent": round(annual_growth, 2),
                "projected_2025": round(last * (1 + annual_growth/100) ** (2025 - values[-1]["year"]), 0)
            }
    
    return analysis


@router.get("/eeu/power-plants")
async def get_eeu_power_plants():
    """Get list of Ethiopian power plants with real data"""
    power_plants = [
        # Hydropower
        {"name": "Grand Ethiopian Renaissance Dam (GERD)", "type": "Hydro", "capacity_mw": 5150, "status": "partial", "commissioned": 2022, "location": "Benishangul-Gumuz"},
        {"name": "Gilgel Gibe III", "type": "Hydro", "capacity_mw": 1870, "status": "operational", "commissioned": 2016, "location": "SNNPR"},
        {"name": "Gilgel Gibe II", "type": "Hydro", "capacity_mw": 420, "status": "operational", "commissioned": 2010, "location": "SNNPR"},
        {"name": "Gilgel Gibe I", "type": "Hydro", "capacity_mw": 184, "status": "operational", "commissioned": 2004, "location": "SNNPR"},
        {"name": "Tekeze", "type": "Hydro", "capacity_mw": 300, "status": "operational", "commissioned": 2009, "location": "Tigray"},
        {"name": "Tana Beles", "type": "Hydro", "capacity_mw": 460, "status": "operational", "commissioned": 2010, "location": "Amhara"},
        {"name": "Fincha-Amerti-Neshe", "type": "Hydro", "capacity_mw": 134, "status": "operational", "commissioned": 2011, "location": "Oromia"},
        {"name": "Koka", "type": "Hydro", "capacity_mw": 43, "status": "operational", "commissioned": 1960, "location": "Oromia"},
        {"name": "Awash II", "type": "Hydro", "capacity_mw": 32, "status": "operational", "commissioned": 1966, "location": "Afar"},
        {"name": "Awash III", "type": "Hydro", "capacity_mw": 32, "status": "operational", "commissioned": 1971, "location": "Afar"},
        {"name": "Melka Wakena", "type": "Hydro", "capacity_mw": 153, "status": "operational", "commissioned": 1988, "location": "Oromia"},
        
        # Wind
        {"name": "Adama I Wind Farm", "type": "Wind", "capacity_mw": 51, "status": "operational", "commissioned": 2011, "location": "Oromia"},
        {"name": "Adama II Wind Farm", "type": "Wind", "capacity_mw": 153, "status": "operational", "commissioned": 2015, "location": "Oromia"},
        {"name": "Ashegoda Wind Farm", "type": "Wind", "capacity_mw": 120, "status": "operational", "commissioned": 2013, "location": "Tigray"},
        
        # Geothermal
        {"name": "Aluto Langano", "type": "Geothermal", "capacity_mw": 7, "status": "operational", "commissioned": 1998, "location": "Oromia"},
        
        # Thermal/Diesel (backup)
        {"name": "Dire Dawa Diesel", "type": "Diesel", "capacity_mw": 38, "status": "standby", "commissioned": 2000, "location": "Dire Dawa"},
        {"name": "Kaliti Diesel", "type": "Diesel", "capacity_mw": 14, "status": "standby", "commissioned": 1999, "location": "Addis Ababa"},
    ]
    
    total_capacity = sum(p["capacity_mw"] for p in power_plants)
    operational_capacity = sum(p["capacity_mw"] for p in power_plants if p["status"] == "operational")
    
    by_type = {}
    for plant in power_plants:
        ptype = plant["type"]
        if ptype not in by_type:
            by_type[ptype] = {"count": 0, "capacity_mw": 0}
        by_type[ptype]["count"] += 1
        by_type[ptype]["capacity_mw"] += plant["capacity_mw"]
    
    return {
        "power_plants": power_plants,
        "summary": {
            "total_plants": len(power_plants),
            "total_capacity_mw": total_capacity,
            "operational_capacity_mw": operational_capacity,
            "by_type": by_type
        },
        "source": "Ethiopian Electric Power (EEP) / EEU Reports"
    }


# ============== FUTURE API INTEGRATION STRUCTURE ==============

class ExternalAPIConfig(BaseModel):
    """Configuration for external API integration"""
    api_name: str
    base_url: str
    api_key: Optional[str] = None
    enabled: bool = False
    rate_limit_per_minute: int = 60


# Placeholder for future EEU API integration
EEU_API_CONFIG = ExternalAPIConfig(
    api_name="EEU_SCADA",
    base_url="https://api.eeu.gov.et",  # Placeholder - not real
    api_key=None,
    enabled=False,
    rate_limit_per_minute=60
)


@router.get("/api-status")
async def get_external_api_status():
    """Check status of external API integrations"""
    return {
        "apis": {
            "openweathermap": {
                "status": "configured" if OPENWEATHER_API_KEY else "not_configured",
                "description": "Real-time weather data for demand forecasting",
                "setup": "Set OPENWEATHER_API_KEY in .env file"
            },
            "eeu_scada": {
                "status": "not_available",
                "description": "Ethiopian Electric Utility SCADA system (future)",
                "note": "EEU does not currently provide public API access"
            },
            "world_bank": {
                "status": "available",
                "description": "World Bank energy statistics",
                "url": "https://data.worldbank.org"
            }
        },
        "data_sources": {
            "weather": "OpenWeatherMap API (or simulated)",
            "historical": "EEU Annual Reports (manually imported)",
            "realtime": "Simulated based on patterns"
        }
    }


@router.post("/configure-api")
async def configure_external_api(config: ExternalAPIConfig):
    """Configure external API (for future use)"""
    # This would store API configuration
    return {
        "message": f"API configuration for {config.api_name} saved",
        "note": "This is a placeholder for future EEU API integration",
        "config": config.dict()
    }


@router.get("/data-quality")
async def get_data_quality_report():
    """Report on data quality and sources"""
    return {
        "report_date": datetime.now().isoformat(),
        "data_sources": [
            {
                "name": "Weather Data",
                "source": "OpenWeatherMap" if OPENWEATHER_API_KEY else "Simulated",
                "quality": "high" if OPENWEATHER_API_KEY else "medium",
                "update_frequency": "30 minutes",
                "coverage": "10 major Ethiopian cities"
            },
            {
                "name": "Historical Demand",
                "source": "EEU Annual Reports",
                "quality": "high",
                "update_frequency": "yearly",
                "coverage": "National aggregate"
            },
            {
                "name": "Real-time Grid Status",
                "source": "Simulated (pattern-based)",
                "quality": "medium",
                "update_frequency": "real-time",
                "note": "Based on typical Ethiopian grid patterns"
            },
            {
                "name": "Power Plant Data",
                "source": "EEP/EEU Public Reports",
                "quality": "high",
                "update_frequency": "as published",
                "coverage": "All major plants"
            }
        ],
        "recommendations": [
            "Configure OpenWeatherMap API for real weather data",
            "Import latest EEU annual report data",
            "Contact EEU for potential data partnership"
        ]
    }
