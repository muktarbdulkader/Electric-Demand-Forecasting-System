"""
Data Preprocessing Module
"""
import pandas as pd
import numpy as np
import os

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and preprocess raw data"""
    df = df.copy()
    df = df.dropna()
    df = df.drop_duplicates()
    
    if 'demand' in df.columns:
        q1 = df['demand'].quantile(0.01)
        q99 = df['demand'].quantile(0.99)
        df = df[(df['demand'] >= q1) & (df['demand'] <= q99)]
    
    return df

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add time-based features from datetime column"""
    df = df.copy()
    
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.dayofweek
        df['month'] = df['datetime'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    return df

def process_raw_data(input_path: str, output_path: str):
    """Process raw data and save cleaned version"""
    df = pd.read_csv(input_path)
    df = add_time_features(df)
    df = clean_data(df)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")
    return df
