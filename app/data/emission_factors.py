"""
Emission factors for carbon calculations.
Based on ICAO, DEFRA 2024, and industry benchmarks.
"""

# =============================================================================
# FLIGHT EMISSION FACTORS
# =============================================================================

# Base emission factors in kg CO₂e per passenger-km
# Aligned with ICAO Carbon Calculator, myclimate, and Google Flights
# 
# These factors include a moderate RF adjustment (~1.1-1.2x baked in)
# to match standard consumer calculator outputs
#
# Source: ICAO Carbon Calculator + myclimate methodology
FLIGHT_FACTORS_PER_KM = {
    "short": {  # < 1,500 km - Higher per-km due to takeoff/landing
        "economy": 0.156,           # ~0.13 base + ~1.2x RF baked in
        "premium_economy": 0.156 * 1.5,
        "business": 0.156 * 3.0,
        "first": 0.156 * 4.0
    },
    "medium": {  # 1,500 - 4,000 km
        "economy": 0.130,           # ~0.11 base + ~1.2x RF baked in
        "premium_economy": 0.130 * 1.5,
        "business": 0.130 * 3.0,
        "first": 0.130 * 4.0
    },
    "long": {  # > 4,000 km (most efficient per-km)
        "economy": 0.111,           # Matches myclimate/Google for long-haul
        "premium_economy": 0.111 * 1.5,
        "business": 0.111 * 3.0,
        "first": 0.111 * 4.0
    }
}

# Radiative Forcing (RF) multiplier
# Set to 1.0 since factors above already include moderate RF adjustment
# For scientific/CSRD reporting, can optionally apply additional 1.5-1.9x
RADIATIVE_FORCING_MULTIPLIER = 1.0

# Average fuel burn rates (kg per km) for estimation
# These are per-flight, not per-passenger
AVERAGE_FUEL_BURN_KG_PER_KM = {
    "short": 3.5,   # Higher per-km due to takeoff/landing
    "medium": 3.0,
    "long": 2.8
}

# Average load factors by airline type
DEFAULT_LOAD_FACTOR = 0.82  # Industry average ~82%


# =============================================================================
# HOTEL EMISSION FACTORS
# =============================================================================

# Energy consumption in kWh per room per night by star rating
# Source: Cornell Hotel Sustainability Benchmarking Index
HOTEL_ENERGY_KWH_PER_NIGHT = {
    1: 25,   # Basic amenities only
    2: 30,   # Standard amenities
    3: 40,   # Air conditioning, minibar typical
    4: 55,   # Spa, restaurant, gym typical
    5: 80    # Luxury amenities, larger rooms
}

# Sustainability certification discount
# Certified hotels typically use 30-40% less energy
ECO_CERTIFIED_DISCOUNT = 0.35


# =============================================================================
# TRAIN EMISSION FACTORS
# =============================================================================

# Emission factors for rail in kg CO₂e per passenger-km
# Source: UIC Railway Handbook, Eurostar sustainability reports
TRAIN_FACTORS_PER_KM = {
    "eurostar": 0.004,       # Eurostar reports 4g CO₂/pkm
    "tgv": 0.003,            # TGV France (nuclear grid)
    "ice": 0.032,            # ICE Germany (mixed grid)
    "uk_rail": 0.035,        # UK average
    "eu_high_speed": 0.015,  # EU high-speed average
    "eu_conventional": 0.041,
    "diesel": 0.089          # Diesel intercity
}


# =============================================================================
# EQUIVALENTS FOR COMMUNICATION
# =============================================================================

# Used to convert kg CO₂e to human-understandable equivalents
# Sources: EPA, various carbon offset providers
EQUIVALENTS = {
    "trees_per_year_kg": 22.0,        # kg CO₂ absorbed by one mature tree per year
    "km_per_kg_driving": 10.0,        # km of average car driving per kg CO₂ (~100g CO₂/km, newer cars)
    "streaming_hours_per_kg": 16.67   # hours of HD streaming per kg CO₂
}


def get_flight_factor(haul_type: str, cabin_class: str) -> float:
    """Get flight emission factor in kg CO₂e per km (without RF)."""
    haul = haul_type.lower()
    cabin = cabin_class.lower()
    
    if haul not in FLIGHT_FACTORS_PER_KM:
        haul = "medium"  # Default to medium
    if cabin not in FLIGHT_FACTORS_PER_KM[haul]:
        cabin = "economy"  # Default to economy
    
    return FLIGHT_FACTORS_PER_KM[haul][cabin]


def get_hotel_energy(star_rating: int) -> float:
    """Get hotel energy consumption in kWh per night."""
    if star_rating < 1:
        star_rating = 1
    elif star_rating > 5:
        star_rating = 5
    return HOTEL_ENERGY_KWH_PER_NIGHT.get(star_rating, 40)


def get_train_factor(train_type: str = "eu_high_speed") -> float:
    """Get train emission factor in kg CO₂e per km."""
    return TRAIN_FACTORS_PER_KM.get(train_type, TRAIN_FACTORS_PER_KM["eu_high_speed"])


def calculate_equivalents(kg_co2: float) -> dict:
    """Convert kg CO₂e to human-readable equivalents."""
    return {
        "trees_to_offset": round(kg_co2 / EQUIVALENTS["trees_per_year_kg"], 1),
        "driving_km": round(kg_co2 * EQUIVALENTS["km_per_kg_driving"], 0),
        "streaming_hours": round(kg_co2 * EQUIVALENTS["streaming_hours_per_kg"], 0)
    }
