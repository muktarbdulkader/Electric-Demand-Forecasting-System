"""
Forecast API Routes - Ethiopian Electric Utility
Real data processing with ML model training
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from datetime import datetime
import pandas as pd
import numpy as np
import io
import sys
import os
import shutil

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.schemas.request import (
    ForecastRequest, ForecastResponse, 
    Forecast24hResponse, HourlyForecast,
    UploadResponse, AnalyticsResponse
)

router = APIRouter(tags=["forecast"])

# Data and model paths
DATA_DIR = os.path.join(backend_dir, 'ml', 'data', 'raw')
MODEL_DIR = os.path.join(backend_dir, 'ml', 'models')
DATA_FILE = os.path.join(DATA_DIR, 'electricity_demand.csv')

# Global predictor and data cache
_predictor = None
_data_cache = None
_last_data_load = None

def load_data():
    """Load the actual data from CSV file"""
    global _data_cache, _last_data_load
    
    if os.path.exists(DATA_FILE):
        file_mtime = os.path.getmtime(DATA_FILE)
        if _data_cache is None or _last_data_load != file_mtime:
            _data_cache = pd.read_csv(DATA_FILE)
            if 'datetime' in _data_cache.columns:
                _data_cache['datetime'] = pd.to_datetime(_data_cache['datetime'])
            _last_data_load = file_mtime
    return _data_cache

def get_predictor(force_reload=False):
    """Get or create predictor, optionally force reload after training"""
    global _predictor
    if _predictor is None or force_reload:
        try:
            from ml.predict import DemandPredictor
            _predictor = DemandPredictor()
        except Exception as e:
            print(f"Error loading predictor: {e}")
            _predictor = DataDrivenPredictor()
    return _predictor

class DataDrivenPredictor:
    """Predictor that uses actual uploaded data"""
    def __init__(self):
        self.data = load_data()
        self._compute_patterns()
    
    def _compute_patterns(self):
        """Compute patterns from actual data"""
        if self.data is None or len(self.data) == 0:
            self.base_demand = 3500
            self.hour_factors = {h: 1.0 for h in range(24)}
            self.day_factors = {d: 1.0 for d in range(7)}
            self.temp_coefficient = 15
            return
        
        # Calculate base demand from data
        self.base_demand = self.data['demand'].mean()
        
        # Calculate hour factors from data
        hour_means = self.data.groupby('hour')['demand'].mean()
        self.hour_factors = {h: hour_means.get(h, self.base_demand) / self.base_demand 
                           for h in range(24)}
        
        # Calculate day of week factors
        if 'day_of_week' in self.data.columns:
            day_means = self.data.groupby('day_of_week')['demand'].mean()
            self.day_factors = {d: day_means.get(d, self.base_demand) / self.base_demand 
                              for d in range(7)}
        else:
            self.day_factors = {d: 1.0 for d in range(7)}
        
        # Calculate temperature coefficient
        if 'temperature' in self.data.columns and len(self.data) > 10:
            temp_corr = np.corrcoef(self.data['temperature'], self.data['demand'])[0, 1]
            self.temp_coefficient = 15 * (1 + temp_corr) if not np.isnan(temp_corr) else 15
        else:
            self.temp_coefficient = 15
    
    def reload_data(self):
        """Reload data after upload"""
        self.data = load_data()
        self._compute_patterns()
    
    def predict(self, temperature, hour, day_of_week, month):
        demand = self.base_demand
        demand *= self.hour_factors.get(hour, 1.0)
        demand *= self.day_factors.get(day_of_week, 1.0)
        demand += (temperature - 25) * self.temp_coefficient
        return round(max(0, demand), 2)
    
    def predict_next_24h(self, base_temp, start_datetime=None):
        if start_datetime is None:
            start_datetime = datetime.now()
        
        predictions = []
        temp_var = [-4, -5, -6, -6, -5, -4, -2, 0, 2, 4, 6, 8,
                    9, 10, 10, 9, 8, 6, 4, 2, 0, -1, -2, -3]
        
        for i in range(24):
            hour = (start_datetime.hour + i) % 24
            dow = (start_datetime.weekday() + (start_datetime.hour + i) // 24) % 7
            month = start_datetime.month
            temp = base_temp + temp_var[hour]
            demand = self.predict(temp, hour, dow, month)
            predictions.append({
                'hour': hour,
                'temperature': round(temp, 1),
                'predicted_demand': round(demand, 2)
            })
        return predictions

def train_model_from_data():
    """Train ML model from current data"""
    try:
        from ml.train import load_data as ml_load_data, prepare_features, train_linear_model, save_model
        
        df = ml_load_data(DATA_FILE)
        if len(df) < 10:
            return False, "Not enough data to train (need at least 10 records)"
        
        X, y, feature_cols = prepare_features(df)
        model, scaler, metrics = train_linear_model(X, y)
        save_model(model, scaler, MODEL_DIR, 'model')
        
        return True, metrics
    except Exception as e:
        return False, str(e)

@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast():
    """Get current hour forecast"""
    try:
        predictor = get_predictor()
        now = datetime.now()
        demand = predictor.predict(
            temperature=25.0,
            hour=now.hour,
            day_of_week=now.weekday(),
            month=now.month
        )
        return ForecastResponse(forecasted_demand=round(demand, 2))
    except Exception as e:
        print(f"Forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/forecast", response_model=ForecastResponse)
async def predict_demand(request: ForecastRequest):
    """Predict demand with custom parameters"""
    try:
        predictor = get_predictor()
        demand = predictor.predict(
            temperature=request.temperature,
            hour=request.hour,
            day_of_week=request.day_of_week,
            month=request.month
        )
        return ForecastResponse(forecasted_demand=round(demand, 2))
    except Exception as e:
        print(f"Predict error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/24h", response_model=Forecast24hResponse)
async def get_24h_forecast(base_temperature: float = 25.0):
    """Get 24-hour forecast"""
    try:
        predictor = get_predictor()
        predictions = predictor.predict_next_24h(base_temperature)
        
        forecasts = [
            HourlyForecast(
                hour=p['hour'],
                temperature=p['temperature'],
                predicted_demand=p['predicted_demand']
            )
            for p in predictions
        ]
        
        demands = [f.predicted_demand for f in forecasts]
        peak_idx = demands.index(max(demands))
        
        return Forecast24hResponse(
            forecasts=forecasts,
            base_temperature=base_temperature,
            total_energy_mwh=round(sum(demands), 2),
            peak_hour=forecasts[peak_idx].hour,
            peak_demand=round(max(demands), 2)
        )
    except Exception as e:
        print(f"24h forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """Get demand analytics"""
    try:
        predictor = get_predictor()
        predictions = predictor.predict_next_24h(25.0)
        demands = [p['predicted_demand'] for p in predictions]
        
        max_idx = demands.index(max(demands))
        min_idx = demands.index(min(demands))
        total_energy = sum(demands)
        cost_per_mwh = 2750
        
        return AnalyticsResponse(
            avg_demand=round(sum(demands) / len(demands), 2),
            max_demand=round(max(demands), 2),
            min_demand=round(min(demands), 2),
            peak_hour=predictions[max_idx]['hour'],
            low_hour=predictions[min_idx]['hour'],
            total_energy_24h=round(total_energy, 2),
            estimated_cost_birr=round(total_energy * cost_per_mwh, 2)
        )
    except Exception as e:
        print(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=UploadResponse)
async def upload_data(file: UploadFile = File(...)):
    """
    Upload CSV data and retrain model
    
    Expected CSV columns:
    - datetime: timestamp (YYYY-MM-DD HH:MM:SS)
    - demand: electricity demand in MW
    - temperature: temperature in Celsius
    - hour: hour of day (0-23)
    - day_of_week: day of week (0=Monday, 6=Sunday)
    - month: month (1-12)
    - humidity: humidity percentage (optional)
    - is_holiday: 1 if holiday, 0 otherwise (optional)
    - region: region name (optional)
    """
    global _predictor, _data_cache, _last_data_load
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files supported")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_cols = ['demand']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing}. Need at least 'demand' column."
            )
        
        # Auto-generate missing columns if possible
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            if 'hour' not in df.columns:
                df['hour'] = df['datetime'].dt.hour
            if 'day_of_week' not in df.columns:
                df['day_of_week'] = df['datetime'].dt.dayofweek
            if 'month' not in df.columns:
                df['month'] = df['datetime'].dt.month
        else:
            # Generate datetime if not present
            if 'hour' not in df.columns:
                df['hour'] = list(range(24)) * (len(df) // 24 + 1)
                df['hour'] = df['hour'][:len(df)]
            if 'day_of_week' not in df.columns:
                df['day_of_week'] = 0
            if 'month' not in df.columns:
                df['month'] = datetime.now().month
            df['datetime'] = pd.date_range(start='2024-01-01', periods=len(df), freq='H')
        
        # Set defaults for optional columns
        if 'temperature' not in df.columns:
            df['temperature'] = 25
        if 'humidity' not in df.columns:
            df['humidity'] = 60
        if 'is_holiday' not in df.columns:
            df['is_holiday'] = 0
        if 'region' not in df.columns:
            df['region'] = 'National'
        
        # Backup existing data
        if os.path.exists(DATA_FILE):
            backup_file = DATA_FILE.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
            shutil.copy(DATA_FILE, backup_file)
            print(f"✅ Backed up data to {backup_file}")
        
        # Save new data (append or replace based on size)
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Option: Append to existing data
        if os.path.exists(DATA_FILE):
            existing_df = pd.read_csv(DATA_FILE)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.drop_duplicates(subset=['datetime'], keep='last', inplace=True)
            combined_df.to_csv(DATA_FILE, index=False)
            total_records = len(combined_df)
            print(f"✅ Appended data. Total records: {total_records}")
        else:
            df.to_csv(DATA_FILE, index=False)
            total_records = len(df)
            print(f"✅ Saved new data. Total records: {total_records}")
        
        # Clear all caches to force reload
        _data_cache = None
        _last_data_load = None
        _predictor = None
        
        print("🔄 Retraining model...")
        # Retrain model with new data
        train_success, train_result = train_model_from_data()
        
        if train_success:
            print(f"✅ Model trained successfully: R²={train_result['r2']:.3f}")
        else:
            print(f"⚠️ Model training issue: {train_result}")
        
        # Force reload predictor with new model
        print("🔄 Reloading predictor...")
        _predictor = get_predictor(force_reload=True)
        
        # Reload patterns in the predictor
        if hasattr(_predictor, 'reload_patterns'):
            _predictor.reload_patterns()
        
        print(f"✅ Predictor reloaded: {type(_predictor).__name__}")
        
        if train_success:
            return UploadResponse(
                message=f"✅ Data uploaded and model retrained! R²={train_result['r2']:.3f}, MAE={train_result['mae']:.1f}MW",
                records_processed=len(df)
            )
        else:
            return UploadResponse(
                message=f"✅ Data uploaded ({total_records} total records). Using pattern-based prediction.",
                records_processed=len(df)
            )
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {error_msg}")


@router.get("/data/stats")
async def get_data_stats():
    """Get statistics about the current training data"""
    df = load_data()
    if df is None or len(df) == 0:
        return {"message": "No data loaded", "records": 0}
    
    return {
        "records": len(df),
        "date_range": {
            "start": str(df['datetime'].min()) if 'datetime' in df.columns else None,
            "end": str(df['datetime'].max()) if 'datetime' in df.columns else None
        },
        "demand_stats": {
            "mean": round(df['demand'].mean(), 2),
            "min": round(df['demand'].min(), 2),
            "max": round(df['demand'].max(), 2),
            "std": round(df['demand'].std(), 2)
        },
        "columns": list(df.columns),
        "regions": df['region'].unique().tolist() if 'region' in df.columns else []
    }


@router.delete("/data/reset")
async def reset_data():
    """Reset data to original sample (for testing)"""
    global _predictor, _data_cache
    
    # Find backup files and restore the oldest one
    backup_files = [f for f in os.listdir(DATA_DIR) if f.startswith('electricity_demand_backup')]
    
    if backup_files:
        backup_files.sort()
        oldest_backup = os.path.join(DATA_DIR, backup_files[0])
        shutil.copy(oldest_backup, DATA_FILE)
        
        _data_cache = None
        _predictor = None
        
        return {"message": f"Data reset to backup: {backup_files[0]}"}
    
    return {"message": "No backup found to restore"}
