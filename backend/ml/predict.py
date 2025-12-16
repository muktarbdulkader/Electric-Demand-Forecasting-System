"""
ML Prediction Module - Ethiopian Electric Utility
Uses trained model from uploaded data
"""
import numpy as np
import pandas as pd
import joblib
import os
from datetime import datetime

class DemandPredictor:
    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.join(os.path.dirname(__file__), 'models')
        
        self.model_dir = model_dir
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data', 'raw')
        self.model = None
        self.scaler = None
        self.use_model = False
        self.n_features = 4
        self.data_patterns = None
        
        self._load_model()
        self._load_data_patterns()
    
    def _load_model(self):
        """Load trained ML model"""
        model_path = os.path.join(self.model_dir, 'model.pkl')
        scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        
        try:
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                if hasattr(self.scaler, 'n_features_in_'):
                    self.n_features = self.scaler.n_features_in_
                self.use_model = True
                print(f"✅ ML model loaded ({self.n_features} features)")
        except Exception as e:
            print(f"⚠️ Could not load model: {e}")
            self.use_model = False
    
    def _load_data_patterns(self):
        """Load patterns from actual data"""
        data_file = os.path.join(self.data_dir, 'electricity_demand.csv')
        
        try:
            if os.path.exists(data_file):
                df = pd.read_csv(data_file)
                
                if len(df) == 0:
                    self._set_default_patterns()
                    return
                
                # Calculate patterns from real data
                self.base_demand = float(df['demand'].mean())
                
                # Hour patterns
                if 'hour' in df.columns:
                    hour_means = df.groupby('hour')['demand'].mean()
                    self.hour_factors = {int(h): float(hour_means.get(h, self.base_demand) / self.base_demand) 
                                       for h in range(24)}
                else:
                    self.hour_factors = {h: 1.0 for h in range(24)}
                
                # Day patterns
                if 'day_of_week' in df.columns:
                    day_means = df.groupby('day_of_week')['demand'].mean()
                    self.day_factors = {int(d): float(day_means.get(d, self.base_demand) / self.base_demand) 
                                      for d in range(7)}
                else:
                    self.day_factors = {d: 1.0 for d in range(7)}
                
                # Temperature coefficient from correlation
                if 'temperature' in df.columns and len(df) > 10:
                    try:
                        corr = np.corrcoef(df['temperature'].dropna(), df['demand'].iloc[:len(df['temperature'].dropna())])[0, 1]
                        self.temp_coef = float(15 * (1 + corr) if not np.isnan(corr) else 15)
                    except:
                        self.temp_coef = 15.0
                else:
                    self.temp_coef = 15.0
                
                self.data_patterns = True
                print(f"✅ Data patterns loaded (base={self.base_demand:.0f}MW, {len(df)} records, temp_coef={self.temp_coef:.1f})")
            else:
                self._set_default_patterns()
        except Exception as e:
            print(f"⚠️ Could not load data patterns: {e}")
            self._set_default_patterns()
            self._set_default_patterns()
    
    def _set_default_patterns(self):
        """Set default patterns when no data available"""
        self.base_demand = 3500.0
        self.hour_factors = {
            0: 0.65, 1: 0.58, 2: 0.52, 3: 0.48, 4: 0.46, 5: 0.50,
            6: 0.62, 7: 0.78, 8: 0.92, 9: 1.02, 10: 1.08, 11: 1.12,
            12: 1.15, 13: 1.12, 14: 1.08, 15: 1.04, 16: 1.00, 17: 1.08,
            18: 1.18, 19: 1.28, 20: 1.22, 21: 1.10, 22: 0.92, 23: 0.78
        }
        self.day_factors = {0: 1.02, 1: 1.04, 2: 1.05, 3: 1.04, 4: 1.02, 5: 0.88, 6: 0.85}
        self.temp_coef = 15.0
        self.data_patterns = False
        print("⚠️ Using default patterns (no data loaded)")
    
    def reload_patterns(self):
        """Reload patterns from data (call after upload)"""
        print("🔄 Reloading data patterns...")
        self._load_model()
        self._load_data_patterns()
        print("✅ Patterns reloaded")
    
    def predict(self, temperature: float, hour: int, day_of_week: int, month: int, 
                humidity: float = 60.0, is_holiday: int = 0) -> float:
        """Predict demand using trained model or data patterns"""
        
        # Try ML model first
        if self.use_model and self.model is not None:
            try:
                features = [temperature, hour, day_of_week, month]
                if self.n_features >= 5:
                    features.append(humidity)
                if self.n_features >= 6:
                    features.append(is_holiday)
                
                X = np.array([features[:self.n_features]])
                X_scaled = self.scaler.transform(X)
                prediction = self.model.predict(X_scaled)[0]
                
                # If model returns 0 or negative, fall back to pattern-based
                if prediction > 100:  # Reasonable minimum demand
                    return round(prediction, 2)
                else:
                    print(f"ML model returned {prediction}, using pattern-based")
            except Exception as e:
                print(f"ML prediction failed: {e}, using pattern-based")
        
        # Pattern-based prediction from actual data
        demand = self.base_demand
        demand *= self.hour_factors.get(hour, 1.0)
        demand *= self.day_factors.get(day_of_week, 1.0)
        
        # Temperature effect (higher temp = more AC usage)
        demand += (temperature - 25) * self.temp_coef
        
        # Humidity effect
        if humidity > 70:
            demand *= 1.02
        
        # Holiday effect
        if is_holiday:
            demand *= 0.85
        
        return round(max(100, demand), 2)  # Minimum 100 MW
    
    def predict_next_24h(self, base_temp: float, start_datetime: datetime = None) -> list:
        """Predict demand for next 24 hours"""
        if start_datetime is None:
            start_datetime = datetime.now()
        
        predictions = []
        # Ethiopian temperature variation pattern
        temp_variation = [-4, -5, -6, -6, -5, -4, -2, 0, 2, 4, 6, 8,
                         9, 10, 10, 9, 8, 6, 4, 2, 0, -1, -2, -3]
        
        for i in range(24):
            hour = (start_datetime.hour + i) % 24
            day_of_week = (start_datetime.weekday() + (start_datetime.hour + i) // 24) % 7
            month = start_datetime.month
            temp = base_temp + temp_variation[hour]
            
            demand = self.predict(temp, hour, day_of_week, month)
            predictions.append({
                'hour': hour,
                'temperature': round(temp, 1),
                'predicted_demand': round(demand, 2)
            })
        
        return predictions
    
    def predict_weekly(self, base_temp: float = 25.0) -> list:
        """Predict demand for next 7 days"""
        from datetime import timedelta
        
        today = datetime.now()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        predictions = []
        
        for i in range(7):
            date = today + timedelta(days=i)
            day_of_week = date.weekday()
            month = date.month
            
            # Calculate daily statistics
            hourly = []
            for hour in range(24):
                temp = base_temp + [-4, -5, -6, -6, -5, -4, -2, 0, 2, 4, 6, 8,
                                    9, 10, 10, 9, 8, 6, 4, 2, 0, -1, -2, -3][hour]
                demand = self.predict(temp, hour, day_of_week, month)
                hourly.append(demand)
            
            predictions.append({
                'day': days[day_of_week],
                'date': date.strftime('%Y-%m-%d'),
                'avg_demand': round(np.mean(hourly), 2),
                'peak_demand': round(max(hourly), 2),
                'min_demand': round(min(hourly), 2),
                'total_energy_mwh': round(sum(hourly), 2),
                'peak_hour': hourly.index(max(hourly))
            })
        
        return predictions
