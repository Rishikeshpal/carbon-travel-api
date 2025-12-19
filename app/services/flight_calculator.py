"""
Flight emission calculator using ICAO methodology.
"""

from typing import Optional
from dataclasses import dataclass

from app.data.airports import (
    get_airport, 
    calculate_distance_km, 
    get_haul_type
)
from app.data.emission_factors import (
    get_flight_factor,
    RADIATIVE_FORCING_MULTIPLIER,
    AVERAGE_FUEL_BURN_KG_PER_KM,
    DEFAULT_LOAD_FACTOR
)


@dataclass
class FlightEmissionResult:
    """Result of flight emission calculation."""
    emissions_kg: float
    distance_km: float
    haul_type: str
    cabin_class: str
    radiative_forcing_multiplier: float
    fuel_burn_kg: float
    load_factor: float
    aircraft_type: Optional[str]
    emission_factor_source: str
    confidence_factors: list[dict]


def calculate_flight_emissions(
    origin: str,
    destination: str,
    cabin_class: str = "economy",
    carrier_code: Optional[str] = None,
    flight_number: Optional[str] = None,
    include_radiative_forcing: bool = True
) -> Optional[FlightEmissionResult]:
    """
    Calculate CO₂e emissions for a flight segment.
    
    Args:
        origin: IATA airport code (e.g., "LHR")
        destination: IATA airport code (e.g., "CDG")
        cabin_class: economy, premium_economy, business, or first
        carrier_code: Optional IATA airline code for carrier-specific factors
        flight_number: Optional flight number for aircraft lookup
        include_radiative_forcing: Whether to apply RF multiplier (default True)
    
    Returns:
        FlightEmissionResult with detailed breakdown, or None if route not found
    """
    # Validate airports exist
    origin_airport = get_airport(origin)
    dest_airport = get_airport(destination)
    
    if not origin_airport or not dest_airport:
        return None
    
    # Calculate distance
    distance_km = calculate_distance_km(origin, destination)
    if not distance_km:
        return None
    
    # Determine haul type
    haul_type = get_haul_type(distance_km)
    
    # Get base emission factor
    base_factor = get_flight_factor(haul_type, cabin_class)
    
    # Apply radiative forcing if requested
    rf_multiplier = RADIATIVE_FORCING_MULTIPLIER if include_radiative_forcing else 1.0
    
    # Calculate total emissions
    emissions_kg = distance_km * base_factor * rf_multiplier
    
    # Estimate fuel burn for this segment
    fuel_burn_kg = distance_km * AVERAGE_FUEL_BURN_KG_PER_KM.get(haul_type, 3.0) / DEFAULT_LOAD_FACTOR
    
    # Build confidence factors
    confidence_factors = []
    
    if carrier_code:
        confidence_factors.append({
            "factor": "carrier_code_provided",
            "impact": "positive",
            "description": f"Carrier {carrier_code} code provided for fleet data lookup"
        })
    
    if haul_type == "short":
        confidence_factors.append({
            "factor": "short_haul_route",
            "impact": "positive",
            "description": "Short-haul routes have well-documented emission factors"
        })
    
    confidence_factors.append({
        "factor": "icao_methodology",
        "impact": "positive",
        "description": "Using ICAO Carbon Calculator methodology with DEFRA 2024 factors"
    })
    
    # Determine aircraft type (simplified - in production, use OAG data)
    aircraft_type = _estimate_aircraft_type(distance_km, carrier_code)
    
    return FlightEmissionResult(
        emissions_kg=round(emissions_kg, 2),
        distance_km=distance_km,
        haul_type=haul_type,
        cabin_class=cabin_class,
        radiative_forcing_multiplier=rf_multiplier,
        fuel_burn_kg=round(fuel_burn_kg, 2),
        load_factor=DEFAULT_LOAD_FACTOR,
        aircraft_type=aircraft_type,
        emission_factor_source="ICAO Carbon Calculator + DEFRA 2024",
        confidence_factors=confidence_factors
    )


def _estimate_aircraft_type(distance_km: float, carrier_code: Optional[str] = None) -> str:
    """
    Estimate likely aircraft type based on route distance.
    In production, this would use OAG schedule data.
    """
    # Common aircraft by route type
    if distance_km < 500:
        return "A320neo"  # or E190
    elif distance_km < 1500:
        return "A320neo"
    elif distance_km < 4000:
        return "A321neo"
    elif distance_km < 8000:
        return "787-9"
    else:
        return "777-300ER"


def get_cabin_class_multiplier(cabin_class: str) -> float:
    """Get the floor space multiplier for a cabin class."""
    multipliers = {
        "economy": 1.0,
        "premium_economy": 1.5,
        "business": 3.0,
        "first": 4.0
    }
    return multipliers.get(cabin_class.lower(), 1.0)
