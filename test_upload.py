#!/usr/bin/env python3
"""
Test script to verify upload functionality works
Run this after starting the backend server
"""
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

API_URL = "http://localhost:8000"

def create_test_data():
    """Create test data"""
    print("📊 Creating test data...")
    dates = pd.date_range('2024-03-01', periods=7*24, freq='H')
    df = pd.DataFrame({
        'datetime': dates,
        'demand': np.random.normal(3500, 500, len(dates)),
        'temperature': 20 + 10*np.sin(np.arange(len(dates))*2*np.pi/(24*7)),
        'hour': dates.hour,
        'day_of_week': dates.dayofweek,
        'month': dates.month,
        'humidity': np.random.normal(60, 10, len(dates)),
        'is_holiday': 0,
        'region': 'National'
    })
    
    df.to_csv('test_upload_data.csv', index=False)
    print(f"✅ Created test_upload_data.csv ({len(df)} records)")
    return df

def test_data_stats():
    """Test getting data stats"""
    print("\n📈 Testing /data/stats endpoint...")
    try:
        response = requests.get(f"{API_URL}/data/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Data stats retrieved:")
            print(f"   Records: {data['records']}")
            print(f"   Demand mean: {data['demand_stats']['mean']:.0f} MW")
            print(f"   Demand range: {data['demand_stats']['min']:.0f} - {data['demand_stats']['max']:.0f} MW")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_forecast_before():
    """Get forecast before upload"""
    print("\n🔮 Getting forecast BEFORE upload...")
    try:
        response = requests.get(f"{API_URL}/forecast/24h")
        if response.status_code == 200:
            data = response.json()
            forecasts = data['forecasts']
            print(f"✅ Got 24h forecast:")
            print(f"   Peak demand: {data['peak_demand']} MW at hour {data['peak_hour']}")
            print(f"   Total energy: {data['total_energy_mwh']} MWh")
            return forecasts
        else:
            print(f"❌ Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_upload(csv_file):
    """Test uploading data"""
    print(f"\n📤 Uploading {csv_file}...")
    try:
        with open(csv_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_URL}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"   Message: {data['message']}")
            print(f"   Records processed: {data['records_processed']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_forecast_after():
    """Get forecast after upload"""
    print("\n🔮 Getting forecast AFTER upload...")
    try:
        response = requests.get(f"{API_URL}/forecast/24h")
        if response.status_code == 200:
            data = response.json()
            forecasts = data['forecasts']
            print(f"✅ Got 24h forecast:")
            print(f"   Peak demand: {data['peak_demand']} MW at hour {data['peak_hour']}")
            print(f"   Total energy: {data['total_energy_mwh']} MWh")
            return forecasts
        else:
            print(f"❌ Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def compare_forecasts(before, after):
    """Compare forecasts before and after"""
    if before is None or after is None:
        print("❌ Cannot compare - missing data")
        return
    
    print("\n📊 Comparing forecasts...")
    before_peak = max([f['predicted_demand'] for f in before])
    after_peak = max([f['predicted_demand'] for f in after])
    
    print(f"   Before peak: {before_peak:.0f} MW")
    print(f"   After peak: {after_peak:.0f} MW")
    print(f"   Difference: {abs(after_peak - before_peak):.0f} MW")
    
    if abs(after_peak - before_peak) > 100:
        print("✅ Forecasts changed significantly - upload worked!")
    else:
        print("⚠️ Forecasts similar - check if data was actually different")

def main():
    print("=" * 60)
    print("🧪 Testing Upload Functionality")
    print("=" * 60)
    
    # Check if server is running
    print("\n🔍 Checking if server is running...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure backend is running: cd backend && uvicorn app.main:app --reload")
        return
    
    # Get initial stats
    test_data_stats()
    
    # Get forecast before upload
    forecast_before = test_forecast_before()
    
    # Create and upload test data
    test_df = create_test_data()
    time.sleep(1)  # Wait a moment
    
    upload_success = test_upload('test_upload_data.csv')
    
    if upload_success:
        time.sleep(2)  # Wait for model to retrain
        
        # Get forecast after upload
        forecast_after = test_forecast_after()
        
        # Compare
        compare_forecasts(forecast_before, forecast_after)
        
        # Get final stats
        test_data_stats()
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
