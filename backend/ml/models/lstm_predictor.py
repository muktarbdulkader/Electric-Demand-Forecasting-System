"""
LSTM Neural Network Predictor - Ethiopian Electric Utility
Deep learning model for complex demand pattern recognition
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

class LSTMPredictor:
    """
    LSTM-based demand predictor
    Note: Uses numpy-based simulation when TensorFlow not available
    """
    
    def __init__(self, model_dir: str = None):
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__))
        self.sequence_length = 24  # 24 hours lookback
        self.model = None
        self.scaler = None
        self.is_trained = False
        self._load_model()
    
    def _load_model(self):
        """Load trained LSTM model if available"""
        try:
            import tensorflow as tf
            model_path = os.path.join(self.model_dir, 'lstm_model.h5')
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                self.is_trained = True
                print("✅ LSTM model loaded")
        except ImportError:
            print("⚠️ TensorFlow not available, using pattern-based LSTM simulation")
            self.is_trained = False
    
    def create_sequences(self, data: np.ndarray, seq_length: int) -> tuple:
        """Create sequences for LSTM training"""
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:i+seq_length])
            y.append(data[i+seq_length])
        return np.array(X), np.array(y)
    
    def train(self, demand_data: np.ndarray, epochs: int = 50):
        """Train LSTM model on demand data"""
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            from sklearn.preprocessing import MinMaxScaler
            
            # Scale data
            self.scaler = MinMaxScaler()
            scaled_data = self.scaler.fit_transform(demand_data.reshape(-1, 1))
            
            # Create sequences
            X, y = self.create_sequences(scaled_data.flatten(), self.sequence_length)
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            # Build model
            self.model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(self.sequence_length, 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            
            # Train
            history = self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=32,
                validation_split=0.2,
                verbose=0
            )
            
            # Save model
            self.model.save(os.path.join(self.model_dir, 'lstm_model.h5'))
            self.is_trained = True
            
            return {
                'final_loss': float(history.history['loss'][-1]),
                'final_mae': float(history.history['mae'][-1]),
                'epochs': epochs
            }
            
        except ImportError:
            print("⚠️ TensorFlow not installed. Using simulation mode.")
            self.is_trained = False
            return {'status': 'simulation_mode', 'message': 'TensorFlow not available'}
    
    def predict(self, recent_demand: list, hours_ahead: int = 24) -> list:
        """Predict future demand using LSTM or pattern simulation"""
        if self.is_trained and self.model is not None:
            return self._predict_with_model(recent_demand, hours_ahead)
        else:
            return self._predict_with_patterns(recent_demand, hours_ahead)
    
    def _predict_with_model(self, recent_demand: list, hours_ahead: int) -> list:
        """Predict using trained LSTM model"""
        predictions = []
        current_sequence = np.array(recent_demand[-self.sequence_length:])
        
        for _ in range(hours_ahead):
            scaled_seq = self.scaler.transform(current_sequence.reshape(-1, 1))
            X = scaled_seq.reshape(1, self.sequence_length, 1)
            pred_scaled = self.model.predict(X, verbose=0)[0][0]
            pred = self.scaler.inverse_transform([[pred_scaled]])[0][0]
            predictions.append(round(float(pred), 2))
            current_sequence = np.append(current_sequence[1:], pred)
        
        return predictions
    
    def _predict_with_patterns(self, recent_demand: list, hours_ahead: int) -> list:
        """Pattern-based prediction when LSTM not available"""
        # Ethiopian demand patterns
        hour_factors = {
            0: 0.65, 1: 0.58, 2: 0.52, 3: 0.48, 4: 0.46, 5: 0.50,
            6: 0.62, 7: 0.78, 8: 0.92, 9: 1.02, 10: 1.08, 11: 1.12,
            12: 1.15, 13: 1.12, 14: 1.08, 15: 1.04, 16: 1.00, 17: 1.08,
            18: 1.18, 19: 1.28, 20: 1.22, 21: 1.10, 22: 0.92, 23: 0.78
        }
        
        base_demand = np.mean(recent_demand) if recent_demand else 3680
        current_hour = datetime.now().hour
        
        predictions = []
        for i in range(hours_ahead):
            hour = (current_hour + i) % 24
            factor = hour_factors.get(hour, 1.0)
            # Add some realistic variation
            noise = np.random.normal(0, base_demand * 0.02)
            pred = base_demand * factor + noise
            predictions.append(round(max(0, pred), 2))
        
        return predictions
    
    def predict_with_confidence(self, recent_demand: list, hours_ahead: int = 24) -> list:
        """Predict with confidence intervals"""
        predictions = self.predict(recent_demand, hours_ahead)
        current_hour = datetime.now().hour
        
        results = []
        for i, pred in enumerate(predictions):
            hour = (current_hour + i) % 24
            # Confidence decreases with forecast horizon
            confidence = max(0.7, 0.95 - (i * 0.01))
            margin = pred * (1 - confidence) * 0.5
            
            results.append({
                'hour': hour,
                'predicted_demand': pred,
                'lower_bound': round(pred - margin, 2),
                'upper_bound': round(pred + margin, 2),
                'confidence': round(confidence, 3)
            })
        
        return results


class ARIMAPredictor:
    """
    ARIMA-based time series predictor
    AutoRegressive Integrated Moving Average for trend analysis
    """
    
    def __init__(self):
        self.model = None
        self.order = (2, 1, 2)  # (p, d, q)
        self.seasonal_order = (1, 1, 1, 24)  # Daily seasonality
        self.is_trained = False
    
    def train(self, demand_data: np.ndarray):
        """Train ARIMA model"""
        try:
            from statsmodels.tsa.arima.model import ARIMA
            from statsmodels.tsa.statespace.sarimax import SARIMAX
            
            # Fit SARIMA model with daily seasonality
            self.model = SARIMAX(
                demand_data,
                order=self.order,
                seasonal_order=self.seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            self.fitted_model = self.model.fit(disp=False)
            self.is_trained = True
            
            return {
                'aic': self.fitted_model.aic,
                'bic': self.fitted_model.bic,
                'status': 'trained'
            }
            
        except ImportError:
            print("⚠️ statsmodels not installed. Using simulation mode.")
            return self._train_simulation(demand_data)
    
    def _train_simulation(self, demand_data: np.ndarray):
        """Simulation training when statsmodels not available"""
        self.base_demand = np.mean(demand_data)
        self.trend = (demand_data[-1] - demand_data[0]) / len(demand_data) if len(demand_data) > 1 else 0
        self.is_trained = True
        return {'status': 'simulation_mode'}
    
    def predict(self, steps: int = 24) -> list:
        """Predict future demand"""
        if self.is_trained and hasattr(self, 'fitted_model'):
            forecast = self.fitted_model.forecast(steps=steps)
            return [round(float(f), 2) for f in forecast]
        else:
            return self._predict_simulation(steps)
    
    def _predict_simulation(self, steps: int) -> list:
        """Pattern-based prediction"""
        hour_factors = {
            0: 0.65, 1: 0.58, 2: 0.52, 3: 0.48, 4: 0.46, 5: 0.50,
            6: 0.62, 7: 0.78, 8: 0.92, 9: 1.02, 10: 1.08, 11: 1.12,
            12: 1.15, 13: 1.12, 14: 1.08, 15: 1.04, 16: 1.00, 17: 1.08,
            18: 1.18, 19: 1.28, 20: 1.22, 21: 1.10, 22: 0.92, 23: 0.78
        }
        
        base = getattr(self, 'base_demand', 3680)
        current_hour = datetime.now().hour
        
        predictions = []
        for i in range(steps):
            hour = (current_hour + i) % 24
            pred = base * hour_factors.get(hour, 1.0)
            predictions.append(round(pred, 2))
        
        return predictions
