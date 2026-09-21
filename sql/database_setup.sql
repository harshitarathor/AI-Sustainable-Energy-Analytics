-- ============================================================
-- database_setup.sql
-- Schema for AI-Sustainable-Energy-Analytics
-- Mirrors data/processed/hourly_energy.csv
-- Target: PostgreSQL (adjust types slightly for MySQL/SQLite if needed)
-- ============================================================

DROP TABLE IF EXISTS hourly_energy;

CREATE TABLE hourly_energy (
    id                          SERIAL PRIMARY KEY,
    timestamp                   TIMESTAMP NOT NULL,
    date                        DATE NOT NULL,
    hour                        SMALLINT NOT NULL CHECK (hour BETWEEN 0 AND 23),
    month                       SMALLINT NOT NULL CHECK (month BETWEEN 1 AND 12),
    is_weekend                  BOOLEAN NOT NULL,

    global_active_power         NUMERIC(8,3) NOT NULL,   -- kW, averaged per hour
    global_reactive_power       NUMERIC(8,3),
    voltage                     NUMERIC(8,3),
    global_intensity            NUMERIC(8,3),

    sub_metering_1              NUMERIC(10,3),           -- Kitchen (Wh)
    sub_metering_2              NUMERIC(10,3),           -- Laundry (Wh)
    sub_metering_3              NUMERIC(10,3),           -- Water heater / AC (Wh)

    -- Feature-engineered columns (from 03_feature_engineering.ipynb)
    previous_hour_consumption   NUMERIC(8,3),
    rolling_avg_3h              NUMERIC(8,3),
    rolling_avg_24h             NUMERIC(8,3),

    -- Populated after anomaly detection (05_anomaly_detection.ipynb)
    hour_mean                   NUMERIC(8,3),
    hour_std                    NUMERIC(8,3),
    z_score_by_hour             NUMERIC(8,3),
    is_anomaly                  BOOLEAN DEFAULT FALSE,

    UNIQUE (timestamp)
);

-- Indexes for the query patterns the dashboard and KPI queries use
CREATE INDEX idx_hourly_energy_date ON hourly_energy (date);
CREATE INDEX idx_hourly_energy_hour ON hourly_energy (hour);
CREATE INDEX idx_hourly_energy_month ON hourly_energy (month);
CREATE INDEX idx_hourly_energy_is_weekend ON hourly_energy (is_weekend);
CREATE INDEX idx_hourly_energy_is_anomaly ON hourly_energy (is_anomaly) WHERE is_anomaly = TRUE;

-- ============================================================
-- Loading data (PostgreSQL example — adjust path as needed)
-- Run from psql, not inside a script that also runs on other engines
-- ============================================================
-- \COPY hourly_energy (timestamp, date, hour, month, is_weekend,
--     global_active_power, global_reactive_power, voltage, global_intensity,
--     sub_metering_1, sub_metering_2, sub_metering_3)
-- FROM 'data/processed/hourly_energy.csv'
-- WITH (FORMAT csv, HEADER true);