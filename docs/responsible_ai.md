# Responsible AI & Project Assumptions

This document outlines the responsible-AI principles, data assumptions, and limitations underlying the AI-Sustainable-Energy-Analytics project.

## Dataset Source

This project uses the **UCI Individual Household Electric Power Consumption** dataset — real electricity-consumption data collected at one-minute intervals from a single household in Sceaux, France (7km from Paris), between December 2006 and November 2010. The dataset is licensed under CC BY 4.0.

This project demonstrates the analytics, anomaly detection, and forecasting approach using real household data. The method is designed to be extensible to other households and small facilities, not limited to the specific household in this dataset.

## Fairness

This system does not label a household as "inefficient" based on absolute consumption alone. Household size, occupancy patterns, climate, regional appliance norms (e.g., electric water heating is common in France but less so elsewhere), and lifestyle naturally differ between homes. Consumption patterns and dominant-category insights observed in this dataset are illustrative of the method, not a universal benchmark for "normal" usage.

## Transparency

All recommendations and AI Assistant answers are generated from **observable, computed consumption statistics** — hourly averages, standard deviations, category totals, and model predictions — not fabricated or invented by an AI language layer. The AI Assistant's responses are template-based explanations built directly from these computed facts, ensuring every claim can be traced back to a specific calculation on the underlying data.

## Privacy

This prototype uses only energy-consumption measurements. It does not use or require any personally identifying information about the household or its occupants.

## Accuracy

Forecasts (produced by the Random Forest model) and savings estimates are **model-based approximations, not guarantees**. Reported model performance (MAE, R²) reflects evaluation on a held-out chronological test split of this specific dataset and may not generalize to other households, climates, or time periods without retraining.

The electricity tariff and CO₂ emission factor used in the Sustainability Impact page are **user-adjustable assumptions**, not fixed facts. Actual values vary by region, country, and energy provider, and should be updated to reflect the user's actual context before relying on cost or emissions figures.

## Anomaly Detection Limitations

Anomalies are flagged using an hour-adjusted Z-score method: a reading is flagged when it deviates more than 2.5 standard deviations from the historical average for that specific hour of day. This method:
- Requires sufficient historical data per hour to produce a stable baseline
- May under-flag genuine anomalies in hours with naturally high variance
- Is a statistical outlier detector, not a diagnostic tool — a flagged reading indicates unusual consumption, not a confirmed appliance fault or specific cause

## Human Oversight

All recommendations, forecasts, and anomaly flags in this system are **decision-support suggestions**, not automated actions or guaranteed outcomes. Users should apply their own judgment and verify context (e.g., a known event like guests staying over, a new appliance, seasonal weather) before treating any flagged anomaly or recommendation as actionable.

## Scope

This is a prototype/demonstration project built on a single publicly available dataset. It has not been validated against multiple households, climates, or real-time data sources, and should not be used for actual energy-management decisions without further validation.