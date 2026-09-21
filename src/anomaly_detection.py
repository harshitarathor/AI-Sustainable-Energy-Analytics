"""
Anomaly detection module for AI-Powered Sustainable Energy Analytics Assistant.
Flags unusual consumption by comparing against hour-specific historical baselines.
"""

import pandas as pd
import numpy as np


def calculate_hourly_baselines(df, consumption_col='Global_active_power', hour_col='hour'):
    """
    Calculates the mean and standard deviation of consumption for each hour of the day.
    Returns a small lookup table used to judge whether new readings are unusual.
    """
    hourly_stats = df.groupby(hour_col)[consumption_col].agg(['mean', 'std']).reset_index()
    hourly_stats.columns = [hour_col, 'hour_mean', 'hour_std']
    return hourly_stats


def flag_anomalies(df, hourly_stats, consumption_col='Global_active_power',
                    hour_col='hour', threshold=2.5):
    """
    Merges hourly baselines into the dataframe and flags readings that deviate
    more than `threshold` standard deviations from their hour's typical average.
    """
    df = df.merge(hourly_stats, on=hour_col, how='left')
    df['z_score_by_hour'] = (df[consumption_col] - df['hour_mean']) / df['hour_std']
    df['is_anomaly'] = df['z_score_by_hour'].abs() > threshold
    return df


def check_single_reading(hourly_stats, hour, actual_consumption, threshold=2.5):
    """
    Checks a single new reading against the hourly baseline table.
    Returns a dictionary with the anomaly verdict and supporting facts —
    this is what gets passed to the recommendation engine / IBM BOB.
    """
    baseline = hourly_stats[hourly_stats['hour'] == hour]

    if baseline.empty:
        return {'is_anomaly': False, 'reason': 'No baseline available for this hour'}

    hour_mean = baseline['hour_mean'].values[0]
    hour_std = baseline['hour_std'].values[0]
    z_score = (actual_consumption - hour_mean) / hour_std
    is_anomaly = abs(z_score) > threshold

    diff_pct = ((actual_consumption - hour_mean) / hour_mean) * 100

    return {
    'is_anomaly': bool(is_anomaly),
    'hour': hour,
    'actual_consumption': actual_consumption,
    'expected_average': round(float(hour_mean), 3),
    'z_score': round(float(z_score), 2),
    'difference_pct': round(float(diff_pct), 1)
}


# Quick test when running this file directly
if __name__ == "__main__":
    df = pd.read_csv('../data/processed/hourly_energy.csv')

    hourly_stats = calculate_hourly_baselines(df)
    print("Hourly baselines calculated.")

    result = check_single_reading(hourly_stats, hour=20, actual_consumption=5.8)
    print(result)