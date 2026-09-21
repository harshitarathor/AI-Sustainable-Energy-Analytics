"""
Forecasting module for AI-Powered Sustainable Energy Analytics Assistant.
Loads the trained model and generates energy consumption predictions.
"""

import joblib
import pandas as pd
import numpy as np


def load_model(model_path='../models/energy_forecasting_model.pkl'):
    """Loads the trained Random Forest forecasting model."""
    model = joblib.load(model_path)
    return model


def prepare_features(hour, month, is_weekend, previous_hour_consumption,
                      rolling_avg_3h, rolling_avg_24h):
    """
    Builds a single-row feature DataFrame matching the format the model was trained on.
    """
    features = pd.DataFrame([{
        'hour': hour,
        'month': month,
        'is_weekend': is_weekend,
        'previous_hour_consumption': previous_hour_consumption,
        'rolling_avg_3h': rolling_avg_3h,
        'rolling_avg_24h': rolling_avg_24h
    }])
    return features


def predict_next_hour(model, hour, month, is_weekend, previous_hour_consumption,
                       rolling_avg_3h, rolling_avg_24h):
    """
    Predicts energy consumption for a given hour based on recent history.
    Returns a single predicted value in kWh.
    """
    features = prepare_features(hour, month, is_weekend, previous_hour_consumption,
                                 rolling_avg_3h, rolling_avg_24h)
    prediction = model.predict(features)[0]
    return round(prediction, 3)


def forecast_from_dataframe(model, df):
    """
    Takes a dataframe with the required feature columns already present
    and returns predictions for every row (used for batch forecasting/dashboard charts).
    """
    features = ['hour', 'month', 'is_weekend', 'previous_hour_consumption',
                'rolling_avg_3h', 'rolling_avg_24h']
    predictions = model.predict(df[features])
    return predictions


# Quick test when running this file directly
if __name__ == "__main__":
    model = load_model('../models/energy_forecasting_model.pkl')

    result = predict_next_hour(
        model,
        hour=20,
        month=12,
        is_weekend=True,
        previous_hour_consumption=2.9,
        rolling_avg_3h=3.1,
        rolling_avg_24h=2.4
    )

    print(f"Predicted consumption for next hour: {result} kWh")