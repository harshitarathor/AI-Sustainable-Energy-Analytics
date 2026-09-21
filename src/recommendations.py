"""
Recommendation Engine for AI-Powered Sustainable Energy Analytics Assistant
Generates evidence-based recommendations from analytics results.
"""

def generate_recommendations(consumption_data):
    """
    Takes computed analytics facts and returns rule-based recommendations.
    consumption_data: dict with keys like 'current_consumption', 'average_consumption',
                       'peak_hour', 'is_anomaly', 'dominant_category', 'forecast_next_hour'
    """
    recommendations = []
    
    # Rule 1: Unusually high consumption
    if consumption_data.get('is_anomaly'):
        recommendations.append(
            "Consumption is unusually high compared to the typical pattern for this hour. "
            "Consider checking for appliances that may have been left running."
        )
    
    # Rule 2: Peak hour usage
    if consumption_data.get('hour') == consumption_data.get('peak_hour'):
        recommendations.append(
            "This is typically your peak usage hour. Reducing non-essential appliance use "
            "during this period can meaningfully lower overall consumption."
        )
    
    # Rule 3: Dominant category
    if consumption_data.get('dominant_category'):
        recommendations.append(
            f"{consumption_data['dominant_category']} accounts for the largest share of your "
            f"tracked consumption. Prioritizing efficiency improvements here would have the biggest impact."
        )
    
    # Rule 4: High forecast
    if consumption_data.get('forecast_next_hour', 0) > consumption_data.get('average_consumption', 0) * 1.3:
        recommendations.append(
            "Your predicted consumption for the next hour is notably higher than average. "
            "Consider reducing non-essential usage during this period."
        )
    
    if not recommendations:
        recommendations.append("Consumption patterns currently look normal — no specific action needed.")
    
    return recommendations


# Quick test when running this file directly
if __name__ == "__main__":
    test_data = {
        'current_consumption': 4.1,
        'average_consumption': 1.09,
        'hour': 20,
        'peak_hour': 20,
        'is_anomaly': True,
        'dominant_category': 'Water Heater/AC',
        'forecast_next_hour': 1.6
    }
    
    for rec in generate_recommendations(test_data):
        print("-", rec)