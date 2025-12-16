"""
Reports & Export System - Ethiopian Electric Utility
Generate PDF, Excel, and CSV reports for demand analytics
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from enum import Enum
import io
import csv
import json

router = APIRouter(prefix="/reports", tags=["reports"])

class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"

class ReportRequest(BaseModel):
    report_type: ReportType
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    regions: Optional[List[str]] = None
    include_forecasts: bool = True
    include_actuals: bool = True
    include_analytics: bool = True

# Ethiopian regions
REGIONS = [
    "Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNPR",
    "Somali", "Afar", "Benishangul-Gumuz", "Gambela", "Harari", "Dire Dawa"
]

def generate_sample_data(start_date: datetime, end_date: datetime) -> List[dict]:
    """Generate sample demand data for reports"""
    data = []
    current = start_date
    hour_factors = {
        0: 0.65, 1: 0.58, 2: 0.52, 3: 0.48, 4: 0.46, 5: 0.50,
        6: 0.62, 7: 0.78, 8: 0.92, 9: 1.02, 10: 1.08, 11: 1.12,
        12: 1.15, 13: 1.12, 14: 1.08, 15: 1.04, 16: 1.00, 17: 1.08,
        18: 1.18, 19: 1.28, 20: 1.22, 21: 1.10, 22: 0.92, 23: 0.78
    }
    
    base_demand = 3680
    while current <= end_date:
        for hour in range(24):
            demand = base_demand * hour_factors[hour]
            # Add some variation
            import random
            demand += random.uniform(-100, 100)
            
            data.append({
                "datetime": current.replace(hour=hour).isoformat(),
                "date": current.strftime("%Y-%m-%d"),
                "hour": hour,
                "demand_mw": round(demand, 2),
                "temperature_c": round(20 + 8 * (hour / 12 if hour < 12 else (24 - hour) / 12), 1),
                "forecast_mw": round(demand * random.uniform(0.95, 1.05), 2),
                "forecast_error_percent": round(random.uniform(-5, 5), 2)
            })
        current += timedelta(days=1)
    
    return data

def calculate_analytics(data: List[dict]) -> dict:
    """Calculate analytics from data"""
    if not data:
        return {}
    
    demands = [d["demand_mw"] for d in data]
    forecasts = [d["forecast_mw"] for d in data]
    errors = [abs(d["forecast_error_percent"]) for d in data]
    
    return {
        "total_records": len(data),
        "date_range": {
            "start": data[0]["date"],
            "end": data[-1]["date"]
        },
        "demand_statistics": {
            "average_mw": round(sum(demands) / len(demands), 2),
            "max_mw": round(max(demands), 2),
            "min_mw": round(min(demands), 2),
            "total_energy_mwh": round(sum(demands), 2)
        },
        "forecast_accuracy": {
            "mae_percent": round(sum(errors) / len(errors), 2),
            "max_error_percent": round(max(errors), 2),
            "accuracy_percent": round(100 - sum(errors) / len(errors), 2)
        },
        "peak_analysis": {
            "peak_hour": max(range(24), key=lambda h: sum(d["demand_mw"] for d in data if d["hour"] == h)),
            "off_peak_hour": min(range(24), key=lambda h: sum(d["demand_mw"] for d in data if d["hour"] == h))
        }
    }

@router.get("/types")
async def get_report_types():
    """Get available report types"""
    return {
        "report_types": [
            {"type": "daily", "description": "24-hour demand report with hourly breakdown"},
            {"type": "weekly", "description": "7-day demand report with daily summaries"},
            {"type": "monthly", "description": "30-day demand report with trends"},
            {"type": "custom", "description": "Custom date range report"}
        ],
        "export_formats": ["csv", "json", "excel"],
        "available_regions": REGIONS
    }

@router.post("/generate")
async def generate_report(request: ReportRequest):
    """Generate a demand report"""
    now = datetime.now()
    
    # Determine date range
    if request.report_type == ReportType.DAILY:
        start_date = now - timedelta(days=1)
        end_date = now
    elif request.report_type == ReportType.WEEKLY:
        start_date = now - timedelta(days=7)
        end_date = now
    elif request.report_type == ReportType.MONTHLY:
        start_date = now - timedelta(days=30)
        end_date = now
    else:
        start_date = datetime.fromisoformat(request.start_date) if request.start_date else now - timedelta(days=7)
        end_date = datetime.fromisoformat(request.end_date) if request.end_date else now
    
    # Generate data
    data = generate_sample_data(start_date, end_date)
    analytics = calculate_analytics(data) if request.include_analytics else None
    
    report = {
        "report_id": f"RPT-{now.strftime('%Y%m%d%H%M%S')}",
        "report_type": request.report_type,
        "generated_at": now.isoformat(),
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "regions": request.regions or ["National"],
        "summary": {
            "total_records": len(data),
            "avg_demand_mw": round(sum(d["demand_mw"] for d in data) / len(data), 2) if data else 0,
            "peak_demand_mw": round(max(d["demand_mw"] for d in data), 2) if data else 0,
            "min_demand_mw": round(min(d["demand_mw"] for d in data), 2) if data else 0,
            "total_energy_mwh": round(sum(d["demand_mw"] for d in data), 2) if data else 0
        }
    }
    
    if request.include_analytics:
        report["analytics"] = analytics
    
    if request.include_forecasts:
        report["forecast_accuracy"] = analytics.get("forecast_accuracy") if analytics else None
    
    return report

@router.get("/export/{format}")
async def export_report(
    format: ExportFormat,
    report_type: ReportType = ReportType.WEEKLY,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Export report in specified format"""
    now = datetime.now()
    
    # Determine date range
    if report_type == ReportType.DAILY:
        start = now - timedelta(days=1)
        end = now
    elif report_type == ReportType.WEEKLY:
        start = now - timedelta(days=7)
        end = now
    elif report_type == ReportType.MONTHLY:
        start = now - timedelta(days=30)
        end = now
    else:
        start = datetime.fromisoformat(start_date) if start_date else now - timedelta(days=7)
        end = datetime.fromisoformat(end_date) if end_date else now
    
    data = generate_sample_data(start, end)
    
    if format == ExportFormat.CSV:
        return export_csv(data, report_type)
    elif format == ExportFormat.JSON:
        return export_json(data, report_type)
    elif format == ExportFormat.EXCEL:
        return export_excel(data, report_type)
    
    raise HTTPException(status_code=400, detail="Invalid format")

def export_csv(data: List[dict], report_type: ReportType) -> StreamingResponse:
    """Export data as CSV"""
    output = io.StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    output.seek(0)
    filename = f"eeu_demand_report_{report_type.value}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

def export_json(data: List[dict], report_type: ReportType) -> StreamingResponse:
    """Export data as JSON"""
    analytics = calculate_analytics(data)
    
    report = {
        "metadata": {
            "report_type": report_type.value,
            "generated_at": datetime.now().isoformat(),
            "total_records": len(data)
        },
        "analytics": analytics,
        "data": data
    }
    
    output = io.StringIO()
    json.dump(report, output, indent=2)
    output.seek(0)
    
    filename = f"eeu_demand_report_{report_type.value}_{datetime.now().strftime('%Y%m%d')}.json"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

def export_excel(data: List[dict], report_type: ReportType) -> StreamingResponse:
    """Export data as Excel (CSV format for compatibility)"""
    # Note: For true Excel format, use openpyxl library
    return export_csv(data, report_type)

@router.get("/daily")
async def get_daily_report():
    """Get daily demand report"""
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    data = generate_sample_data(yesterday, now)
    
    # Group by hour
    hourly_summary = {}
    for d in data:
        hour = d["hour"]
        if hour not in hourly_summary:
            hourly_summary[hour] = {"demands": [], "forecasts": []}
        hourly_summary[hour]["demands"].append(d["demand_mw"])
        hourly_summary[hour]["forecasts"].append(d["forecast_mw"])
    
    hourly_data = []
    for hour in range(24):
        if hour in hourly_summary:
            demands = hourly_summary[hour]["demands"]
            forecasts = hourly_summary[hour]["forecasts"]
            hourly_data.append({
                "hour": hour,
                "avg_demand_mw": round(sum(demands) / len(demands), 2),
                "avg_forecast_mw": round(sum(forecasts) / len(forecasts), 2),
                "accuracy_percent": round(100 - abs(sum(demands) - sum(forecasts)) / sum(demands) * 100, 2)
            })
    
    return {
        "report_type": "daily",
        "date": yesterday.strftime("%Y-%m-%d"),
        "generated_at": now.isoformat(),
        "hourly_data": hourly_data,
        "summary": {
            "total_energy_mwh": round(sum(d["demand_mw"] for d in data), 2),
            "peak_demand_mw": round(max(d["demand_mw"] for d in data), 2),
            "peak_hour": max(hourly_data, key=lambda x: x["avg_demand_mw"])["hour"],
            "min_demand_mw": round(min(d["demand_mw"] for d in data), 2),
            "avg_accuracy_percent": round(sum(h["accuracy_percent"] for h in hourly_data) / 24, 2)
        }
    }

@router.get("/weekly")
async def get_weekly_report():
    """Get weekly demand report"""
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    data = generate_sample_data(week_ago, now)
    
    # Group by date
    daily_summary = {}
    for d in data:
        date = d["date"]
        if date not in daily_summary:
            daily_summary[date] = []
        daily_summary[date].append(d["demand_mw"])
    
    daily_data = []
    for date, demands in sorted(daily_summary.items()):
        daily_data.append({
            "date": date,
            "avg_demand_mw": round(sum(demands) / len(demands), 2),
            "peak_demand_mw": round(max(demands), 2),
            "min_demand_mw": round(min(demands), 2),
            "total_energy_mwh": round(sum(demands), 2)
        })
    
    return {
        "report_type": "weekly",
        "week_start": week_ago.strftime("%Y-%m-%d"),
        "week_end": now.strftime("%Y-%m-%d"),
        "generated_at": now.isoformat(),
        "daily_data": daily_data,
        "summary": {
            "total_energy_mwh": round(sum(d["total_energy_mwh"] for d in daily_data), 2),
            "avg_daily_demand_mw": round(sum(d["avg_demand_mw"] for d in daily_data) / len(daily_data), 2),
            "peak_day": max(daily_data, key=lambda x: x["peak_demand_mw"])["date"],
            "peak_demand_mw": round(max(d["peak_demand_mw"] for d in daily_data), 2)
        }
    }

@router.get("/regional")
async def get_regional_report():
    """Get regional demand breakdown report"""
    now = datetime.now()
    
    regional_data = {
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
    
    regions = []
    total_demand = 0
    for region, data in regional_data.items():
        demand = data["base_demand"]
        total_demand += demand
        regions.append({
            "region": region,
            "current_demand_mw": demand,
            "population": data["population"],
            "households": data["households"],
            "per_capita_kw": round((demand * 1000) / data["population"], 4),
            "share_percent": 0  # Will calculate after
        })
    
    # Calculate share percentages
    for r in regions:
        r["share_percent"] = round((r["current_demand_mw"] / total_demand) * 100, 2)
    
    return {
        "report_type": "regional",
        "generated_at": now.isoformat(),
        "regions": sorted(regions, key=lambda x: x["current_demand_mw"], reverse=True),
        "national_summary": {
            "total_demand_mw": total_demand,
            "total_population": sum(r["population"] for r in regions),
            "total_households": sum(r["households"] for r in regions),
            "regions_count": len(regions)
        }
    }
