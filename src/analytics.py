"""
Analytics module for AI-Powered Sustainable Energy Analytics Assistant.
Provides KPI calculations and summary statistics used across the dashboard.
"""

import pandas as pd


def get_basic_kpis(df, consumption_col='Global_active_power'):
    """Returns total, average, max, and min consumption."""
    return {
        'total_consumption': round(float(df[consumption_col].sum()), 2),
        'avg_consumption': round(float(df[consumption_col].mean()), 2),
        'max_consumption': round(float(df[consumption_col].max()), 2),
        'min_consumption': round(float(df[consumption_col].min()), 2)
    }


def get_peak_hour(df, consumption_col='Global_active_power', hour_col='hour'):
    """Returns the hour of day with the highest average consumption."""
    hourly_avg = df.groupby(hour_col)[consumption_col].mean()
    peak_hour = hourly_avg.idxmax()
    peak_value = round(float(hourly_avg.max()), 2)
    return {'peak_hour': int(peak_hour), 'peak_avg_consumption': peak_value}


def get_weekday_weekend_comparison(df, consumption_col='Global_active_power',
                                    weekend_col='is_weekend'):
    """Returns average consumption split by weekday vs weekend."""
    comparison = df.groupby(weekend_col)[consumption_col].mean()
    return {
        'weekday_avg': round(float(comparison.get(False, 0)), 2),
        'weekend_avg': round(float(comparison.get(True, 0)), 2)
    }


def get_category_breakdown(df):
    """Returns total consumption for each sub-metering category."""
    return {
        'kitchen': round(float(df['Sub_metering_1'].sum()), 2),
        'laundry': round(float(df['Sub_metering_2'].sum()), 2),
        'water_heater_ac': round(float(df['Sub_metering_3'].sum()), 2)
    }


def get_dominant_category(df):
    """Returns the name of the category with the highest total consumption."""
    breakdown = get_category_breakdown(df)
    dominant = max(breakdown, key=breakdown.get)
    label_map = {
        'kitchen': 'Kitchen',
        'laundry': 'Laundry',
        'water_heater_ac': 'Water Heater/AC'
    }
    return label_map[dominant]


# Quick test when running this file directly
if __name__ == "__main__":
    df = pd.read_csv('../data/processed/hourly_energy.csv')

    print("Basic KPIs:", get_basic_kpis(df))
    print("Peak hour:", get_peak_hour(df))
    print("Weekday vs Weekend:", get_weekday_weekend_comparison(df))
    print("Category breakdown:", get_category_breakdown(df))
    print("Dominant category:", get_dominant_category(df))