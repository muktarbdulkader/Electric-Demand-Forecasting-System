"""
ML Training Module - Ethiopian Electric Utility
Trains Linear Regression, Random Forest, and prepares for LSTM/ARIMA
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os

def load_data(filepath: str) -> pd.DataFrame:
    """Load electricity demand data from CSV"""
    df = pd.read_csv(filepath)
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
    return df

def prepare_features(df: pd.DataFrame) -> tuple:
    """Prepare features and target for training"""
    feature_cols = ['temperature', 'hour', 'day_of_week', 'month']
    
    # Add humidity if available
    if 'humidity' in df.columns:
        feature_cols.append('humidity')
    
    # Add holiday flag if available
    if 'is_holiday' in df.columns:
        feature_cols.append('is_holiday')
    
    X = df[feature_cols].values
    y = df['demand'].values
    return X, y, feature_cols

def train_linear_model(X: np.ndarray, y: np.ndarray) -> tuple:
    """Train Linear Regression model"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    
    metrics = {
        'mae': mean_absolute_error(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'mape': np.mean(np.abs((y_test - y_pred) / y_test)) * 100,
        'r2': r2_score(y_test, y_pred)
    }
    
    return model, scaler, metrics

def train_random_forest(X: np.ndarray, y: np.ndarray) -> tuple:
    """Train Random Forest model"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    metrics = {
        'mae': mean_absolute_error(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'mape': np.mean(np.abs((y_test - y_pred) / y_test)) * 100,
        'r2': r2_score(y_test, y_pred)
    }
    
    return model, metrics

def save_model(model, scaler, model_dir: str, model_name: str = 'model'):
    """Save trained model and scaler"""
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, f'{model_name}.pkl'))
    if scaler:
        joblib.dump(scaler, os.path.join(model_dir, 'scaler.pkl'))
    print(f"Model saved to {model_dir}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data', 'raw', 'electricity_demand.csv')
    model_dir = os.path.join(base_dir, 'models')
    
    print("=" * 60)
    print("Ethiopian Electric Utility - ML Model Training")
    print("=" * 60)
    
    print("\n📊 Loading data...")
    df = load_data(data_path)
    print(f"   Loaded {len(df)} records")
    
    print("\n🔧 Preparing features...")
    X, y, feature_cols = prepare_features(df)
    print(f"   Features: {feature_cols}")
    
    print("\n🤖 Training Linear Regression...")
    lr_model, scaler, lr_metrics = train_linear_model(X, y)
    print(f"   MAE:  {lr_metrics['mae']:.2f} MW")
    print(f"   RMSE: {lr_metrics['rmse']:.2f} MW")
    print(f"   MAPE: {lr_metrics['mape']:.2f}%")
    print(f"   R²:   {lr_metrics['r2']:.4f}")
    
    print("\n🌲 Training Random Forest...")
    rf_model, rf_metrics = train_random_forest(X, y)
    print(f"   MAE:  {rf_metrics['mae']:.2f} MW")
    print(f"   RMSE: {rf_metrics['rmse']:.2f} MW")
    print(f"   MAPE: {rf_metrics['mape']:.2f}%")
    print(f"   R²:   {rf_metrics['r2']:.4f}")
    
    # Save best model (Linear Regression for simplicity)
    print("\n💾 Saving models...")
    save_model(lr_model, scaler, model_dir, 'model')
    save_model(rf_model, None, model_dir, 'rf_model')
    
    print("\n✅ Training complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
