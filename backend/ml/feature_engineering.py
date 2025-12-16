"""
Feature Engineering Module
"""
import pandas as pd
import numpy as np

def create_lag_features(df: pd.DataFrame, column: str, lags: list) -> pd.DataFrame:
    """Create lag features for time series"""
    df = df.copy()
    for lag in lags:
        df[f'{column}_lag_{lag}'] = df[column].shift(lag)
    return df

def create_rolling_features(df: pd.DataFrame, column: str, windows: list) -> pd.DataFrame:
    """Create rolling statistics features"""
    df = df.copy()
    for window in windows:
        df[f'{column}_rolling_mean_{window}'] = df[column].rolling(window=window).mean()
        df[f'{column}_rolling_std_{window}'] = df[column].rolling(window=window).std()
    return df

def create_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create cyclical encoding for time features"""
    df = df.copy()
    
    if 'hour' in df.columns:
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    if 'day_of_week' in df.columns:
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    if 'month' in df.columns:
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    return df
