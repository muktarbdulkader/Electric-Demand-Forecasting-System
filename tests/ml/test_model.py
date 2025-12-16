"""
ML Model Tests
"""
import pytest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

def test_model_files_exist():
    """Test that trained model files exist"""
    model_dir = os.path.join(os.path.dirname(__file__), '../../backend/ml/models')
    assert os.path.exists(os.path.join(model_dir, 'model.pkl')), "Model file not found"
    assert os.path.exists(os.path.join(model_dir, 'scaler.pkl')), "Scaler file not found"

def test_predictor_initialization():
    """Test DemandPredictor can be initialized"""
    from ml.predict import DemandPredictor
    predictor = DemandPredictor()
    assert predictor.model is not None
    assert predictor.scaler is not None

def test_single_prediction():
    """Test single prediction returns valid value"""
    from ml.predict import DemandPredictor
    predictor = DemandPredictor()
    
    result = predictor.predict(
        temperature=15.0,
        hour=12,
        day_of_week=2,
        month=6
    )
    
    assert isinstance(result, (int, float))
    assert result >= 0  # Demand should be non-negative

def test_24h_prediction():
    """Test 24-hour prediction returns correct structure"""
    from ml.predict import DemandPredictor
    predictor = DemandPredictor()
    
    predictions = predictor.predict_next_24h(base_temp=15.0)
    
    assert len(predictions) == 24
    for p in predictions:
        assert 'hour' in p
        assert 'temperature' in p
        assert 'predicted_demand' in p
        assert 0 <= p['hour'] <= 23
        assert p['predicted_demand'] >= 0

def test_prediction_varies_with_input():
    """Test that predictions change with different inputs"""
    from ml.predict import DemandPredictor
    predictor = DemandPredictor()
    
    pred1 = predictor.predict(temperature=5, hour=3, day_of_week=0, month=1)
    pred2 = predictor.predict(temperature=30, hour=14, day_of_week=3, month=7)
    
    assert pred1 != pred2, "Predictions should vary with different inputs"
