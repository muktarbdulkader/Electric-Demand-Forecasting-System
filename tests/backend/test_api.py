"""
Backend API Tests
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_forecast():
    response = client.get("/forecast")
    assert response.status_code == 200
    data = response.json()
    assert "forecasted_demand" in data
    assert isinstance(data["forecasted_demand"], (int, float))

def test_post_forecast():
    payload = {
        "temperature": 20.0,
        "hour": 14,
        "day_of_week": 2,
        "month": 6
    }
    response = client.post("/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "forecasted_demand" in data

def test_get_24h_forecast():
    response = client.get("/forecast/24h?base_temperature=15")
    assert response.status_code == 200
    data = response.json()
    assert "forecasts" in data
    assert len(data["forecasts"]) == 24

def test_get_analytics():
    response = client.get("/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "avg_demand" in data
    assert "max_demand" in data
    assert "min_demand" in data
    assert "peak_hour" in data
    assert "low_hour" in data

def test_invalid_forecast_params():
    payload = {
        "temperature": 20.0,
        "hour": 25,  # Invalid hour
        "day_of_week": 2,
        "month": 6
    }
    response = client.post("/forecast", json=payload)
    assert response.status_code == 422  # Validation error
