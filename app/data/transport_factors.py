"""
Ground transport emission factors.
Based on DEFRA 2024, EPA, and local transport authority data.
"""

# =============================================================================
# GROUND TRANSPORT EMISSION FACTORS
# =============================================================================

# Emission factors in kg CO₂e per kilometer
# Source: DEFRA 2024 UK Government GHG Conversion Factors

CAR_FACTORS_PER_KM = {
    # Private/Taxi vehicles
    "taxi": 0.149,              # Average taxi (petrol/diesel mix)
    "uber_x": 0.121,            # UberX / economy rideshare (newer fleet)
    "uber_xl": 0.180,           # UberXL / larger vehicle
    "uber_black": 0.195,        # Premium sedan
    "private_car_petrol": 0.170,  # Average petrol car
    "private_car_diesel": 0.163,  # Average diesel car
    "private_car_hybrid": 0.106,  # Hybrid vehicle
    "electric_car": 0.053,      # Electric vehicle (grid average)
    "electric_uber": 0.048,     # Tesla/EV rideshare
    
    # Shared transport
    "bus": 0.089,               # Average local bus
    "coach": 0.027,             # Long-distance coach
    "metro": 0.029,             # Underground/Metro
    "tram": 0.032,              # Light rail/Tram
}

# Airport transfer typical distances (km) - one way
AIRPORT_TRANSFER_DISTANCES = {
    # Europe
    "LHR": {"city": "London", "distance_km": 25, "typical_fare_eur": 60},
    "LGW": {"city": "London", "distance_km": 45, "typical_fare_eur": 80},
    "CDG": {"city": "Paris", "distance_km": 32, "typical_fare_eur": 55},
    "ORY": {"city": "Paris", "distance_km": 18, "typical_fare_eur": 35},
    "FRA": {"city": "Frankfurt", "distance_km": 14, "typical_fare_eur": 40},
    "MUC": {"city": "Munich", "distance_km": 38, "typical_fare_eur": 70},
    "AMS": {"city": "Amsterdam", "distance_km": 20, "typical_fare_eur": 45},
    "FCO": {"city": "Rome", "distance_km": 32, "typical_fare_eur": 50},
    "MXP": {"city": "Milan", "distance_km": 50, "typical_fare_eur": 90},
    "BCN": {"city": "Barcelona", "distance_km": 18, "typical_fare_eur": 40},
    "MAD": {"city": "Madrid", "distance_km": 17, "typical_fare_eur": 35},
    "DUB": {"city": "Dublin", "distance_km": 12, "typical_fare_eur": 30},
    
    # Middle East
    "DXB": {"city": "Dubai", "distance_km": 15, "typical_fare_eur": 25},
    "DOH": {"city": "Doha", "distance_km": 22, "typical_fare_eur": 30},
    
    # Asia
    "SIN": {"city": "Singapore", "distance_km": 22, "typical_fare_eur": 20},
    "HKG": {"city": "Hong Kong", "distance_km": 35, "typical_fare_eur": 35},
    "NRT": {"city": "Tokyo", "distance_km": 70, "typical_fare_eur": 180},
    "HND": {"city": "Tokyo", "distance_km": 20, "typical_fare_eur": 50},
    "BKK": {"city": "Bangkok", "distance_km": 30, "typical_fare_eur": 15},
    
    # USA
    "JFK": {"city": "New York", "distance_km": 26, "typical_fare_eur": 60},
    "EWR": {"city": "New York", "distance_km": 28, "typical_fare_eur": 65},
    "LAX": {"city": "Los Angeles", "distance_km": 27, "typical_fare_eur": 50},
    "SFO": {"city": "San Francisco", "distance_km": 21, "typical_fare_eur": 55},
    "ORD": {"city": "Chicago", "distance_km": 27, "typical_fare_eur": 45},
}

# Default airport transfer distance if not in database
DEFAULT_AIRPORT_DISTANCE_KM = 25


# =============================================================================
# HOTEL ADDITIONAL FACTORS
# =============================================================================

# Breakfast emission factors (kg CO₂e per person per breakfast)
# Source: Various LCA studies on hotel food service
BREAKFAST_FACTORS = {
    "none": 0.0,
    "continental": 0.8,      # Light breakfast (pastries, coffee, juice)
    "buffet": 2.2,           # Full buffet breakfast
    "full_english": 2.8,     # Full cooked breakfast
    "vegan": 0.5,            # Plant-based breakfast
}

# Room service / amenity factors (kg CO₂e per night)
AMENITY_FACTORS = {
    "standard": 0.0,         # No extra services
    "daily_cleaning": 1.2,   # Daily room cleaning
    "laundry": 2.5,          # Laundry service per use
    "spa": 5.0,              # Spa/pool usage per session
    "gym": 0.8,              # Gym usage
}


def get_car_emission_factor(vehicle_type: str) -> float:
    """Get emission factor for a vehicle type in kg CO₂e per km."""
    return CAR_FACTORS_PER_KM.get(vehicle_type, CAR_FACTORS_PER_KM["taxi"])


def calculate_transfer_emissions(
    airport_code: str,
    vehicle_type: str = "taxi",
    is_round_trip: bool = True
) -> dict:
    """
    Calculate emissions for airport transfer.
    
    Args:
        airport_code: IATA airport code
        vehicle_type: Type of vehicle (taxi, uber_x, etc.)
        is_round_trip: Whether to double for return journey
    
    Returns:
        Dictionary with emissions and details
    """
    airport_data = AIRPORT_TRANSFER_DISTANCES.get(
        airport_code.upper(),
        {"city": "Unknown", "distance_km": DEFAULT_AIRPORT_DISTANCE_KM}
    )
    
    distance = airport_data["distance_km"]
    if is_round_trip:
        distance *= 2
    
    factor = get_car_emission_factor(vehicle_type)
    emissions = distance * factor
    
    return {
        "emissions_kg": round(emissions, 2),
        "distance_km": distance,
        "vehicle_type": vehicle_type,
        "factor_per_km": factor,
        "city": airport_data.get("city", "Unknown")
    }


def calculate_city_transport_emissions(
    distance_km: float,
    vehicle_type: str = "uber_x"
) -> dict:
    """
    Calculate emissions for city transport (Uber, taxi, etc.)
    
    Args:
        distance_km: Total distance in kilometers
        vehicle_type: Type of vehicle
    
    Returns:
        Dictionary with emissions and details
    """
    factor = get_car_emission_factor(vehicle_type)
    emissions = distance_km * factor
    
    return {
        "emissions_kg": round(emissions, 2),
        "distance_km": distance_km,
        "vehicle_type": vehicle_type,
        "factor_per_km": factor
    }


def calculate_breakfast_emissions(
    breakfast_type: str,
    nights: int,
    persons: int
) -> dict:
    """
    Calculate emissions from hotel breakfast.
    
    Args:
        breakfast_type: Type of breakfast (continental, buffet, etc.)
        nights: Number of nights (= number of breakfasts)
        persons: Number of persons
    
    Returns:
        Dictionary with emissions and details
    """
    factor = BREAKFAST_FACTORS.get(breakfast_type, 0.0)
    emissions = factor * nights * persons
    
    return {
        "emissions_kg": round(emissions, 2),
        "breakfast_type": breakfast_type,
        "breakfasts_count": nights * persons,
        "factor_per_breakfast": factor
    }
