-- ============================================================
-- analysis_queries.sql
-- Deeper analysis: sustainability estimates, data quality checks
-- ============================================================

-- 1. Estimated cost & CO2 impact (mirrors 5_Sustainability.py)
-- Replace :tariff and :co2_factor with your chosen assumptions
-- (e.g. tariff = 8.0 INR/kWh, co2_factor = 0.82 kg/kWh)
SELECT
    ROUND(SUM(global_active_power)::numeric, 2) AS total_kwh,
    ROUND(SUM(global_active_power) * 8.0, 2) AS estimated_cost,
    ROUND(SUM(global_active_power) * 0.82, 2) AS estimated_co2_kg
FROM hourly_energy;


-- 2. Potential savings scenario at a target reduction % (e.g. 8%)
SELECT
    ROUND(SUM(global_active_power)::numeric, 2) AS total_kwh,
    ROUND(SUM(global_active_power) * 0.08, 2) AS potential_kwh_saved,
    ROUND(SUM(global_active_power) * 0.08 * 8.0, 2) AS potential_cost_saved,
    ROUND(SUM(global_active_power) * 0.08 * 0.82, 2) AS potential_co2_saved_kg
FROM hourly_energy;


-- 3. Data quality overview (mirrors the Data Quality cards on Consumption Analysis page)
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE global_active_power IS NULL) AS missing_power_readings,
    COUNT(*) - COUNT(DISTINCT timestamp) AS duplicate_timestamps
FROM hourly_energy;


-- 4. Consumption trend by year (useful since this dataset spans multiple years —
-- helps check whether the forecasting model needs a year/trend feature)
SELECT
    EXTRACT(YEAR FROM date) AS year,
    ROUND(AVG(global_active_power)::numeric, 2) AS avg_consumption,
    COUNT(*) AS hours_recorded
FROM hourly_energy
GROUP BY EXTRACT(YEAR FROM date)
ORDER BY year;


-- 5. Hour x day-type consumption matrix (useful for a heatmap visualization)
SELECT
    hour,
    is_weekend,
    ROUND(AVG(global_active_power)::numeric, 2) AS avg_consumption
FROM hourly_energy
GROUP BY hour, is_weekend
ORDER BY hour, is_weekend;