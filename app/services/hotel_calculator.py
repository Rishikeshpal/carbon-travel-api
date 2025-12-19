"""
Hotel emission calculator using regional grid carbon intensity.
Includes room energy, breakfast, and amenities.
"""

from typing import Optional
from dataclasses import dataclass
from datetime import date

from app.data.grid_intensity import get_grid_intensity, get_intensity_value
from app.data.emission_factors import (
    get_hotel_energy,
    ECO_CERTIFIED_DISCOUNT
)
from app.data.transport_factors import (
    calculate_breakfast_emissions,
    BREAKFAST_FACTORS
)


@dataclass
class HotelEmissionResult:
    """Result of hotel emission calculation."""
    emissions_kg: float
    nights: int
    rooms: int
    persons: int
    emissions_per_night_kg: float
    energy_consumption_kwh: float
    grid_carbon_intensity: dict
    star_rating: int
    sustainability_certified: bool
    breakfast_emissions_kg: float
    breakfast_type: str
    emission_factor_source: str
    confidence_factors: list[dict]


def calculate_hotel_emissions(
    country_code: str,
    check_in: date,
    check_out: date,
    star_rating: int = 3,
    room_count: int = 1,
    persons: int = 1,
    sustainability_certified: bool = False,
    breakfast_type: str = "none",
    hotel_chain: Optional[str] = None
) -> HotelEmissionResult:
    """
    Calculate CO₂e emissions for a hotel stay.
    
    Args:
        country_code: ISO 3166-1 alpha-2 country code
        check_in: Check-in date
        check_out: Check-out date
        star_rating: Hotel star rating (1-5)
        room_count: Number of rooms
        persons: Number of persons (for breakfast calculation)
        sustainability_certified: Whether hotel has eco certification
        breakfast_type: Type of breakfast (none, continental, buffet, full_english, vegan)
        hotel_chain: Optional hotel chain for chain-specific factors
    
    Returns:
        HotelEmissionResult with detailed breakdown
    """
    # Calculate number of nights
    nights = (check_out - check_in).days
    if nights < 1:
        nights = 1
    
    # Clamp star rating
    star_rating = max(1, min(5, star_rating))
    
    # Get energy consumption per room per night
    energy_kwh_per_night = get_hotel_energy(star_rating)
    
    # Apply sustainability certification discount
    if sustainability_certified:
        energy_kwh_per_night *= (1 - ECO_CERTIFIED_DISCOUNT)
    
    # Get grid carbon intensity for the country
    grid_data = get_grid_intensity(country_code)
    intensity_g_per_kwh = grid_data["intensity"]
    
    # Calculate total energy consumption
    total_energy_kwh = energy_kwh_per_night * nights * room_count
    
    # Calculate room emissions (convert g to kg)
    room_emissions_kg = (total_energy_kwh * intensity_g_per_kwh) / 1000
    
    # Calculate breakfast emissions
    breakfast_result = calculate_breakfast_emissions(breakfast_type, nights, persons)
    breakfast_emissions_kg = breakfast_result["emissions_kg"]
    
    # Total emissions
    emissions_kg = room_emissions_kg + breakfast_emissions_kg
    
    # Emissions per night (for single room, excluding breakfast)
    emissions_per_night = (energy_kwh_per_night * intensity_g_per_kwh) / 1000
    
    # Build confidence factors
    confidence_factors = []
    
    if grid_data.get("quality") == "measured":
        confidence_factors.append({
            "factor": "measured_grid_data",
            "impact": "positive",
            "description": f"Using measured grid carbon intensity for {country_code}"
        })
    elif grid_data.get("quality") == "estimated":
        confidence_factors.append({
            "factor": "estimated_grid_data",
            "impact": "neutral",
            "description": f"Using estimated grid carbon intensity for {country_code}"
        })
    else:
        confidence_factors.append({
            "factor": "default_grid_data",
            "impact": "negative",
            "description": "Using IPCC global default for grid carbon intensity"
        })
    
    if sustainability_certified:
        confidence_factors.append({
            "factor": "eco_certification",
            "impact": "positive",
            "description": "Sustainability certification reduces estimated energy use by 35%"
        })
    
    confidence_factors.append({
        "factor": "hotel_benchmark",
        "impact": "positive",
        "description": "Using Cornell HSBI energy benchmarks by star rating"
    })
    
    if breakfast_type != "none":
        confidence_factors.append({
            "factor": "breakfast_included",
            "impact": "neutral",
            "description": f"Breakfast ({breakfast_type}) emissions included"
        })
    
    return HotelEmissionResult(
        emissions_kg=round(emissions_kg, 2),
        nights=nights,
        rooms=room_count,
        persons=persons,
        emissions_per_night_kg=round(emissions_per_night, 2),
        energy_consumption_kwh=round(total_energy_kwh, 2),
        grid_carbon_intensity={
            "value": intensity_g_per_kwh,
            "source": grid_data.get("source", "IEA"),
            "country": country_code
        },
        star_rating=star_rating,
        sustainability_certified=sustainability_certified,
        breakfast_emissions_kg=round(breakfast_emissions_kg, 2),
        breakfast_type=breakfast_type,
        emission_factor_source="Cornell HSBI + Grid intensity data",
        confidence_factors=confidence_factors
    )


def compare_hotel_emissions(
    country_code: str,
    nights: int,
    star_rating: int = 3
) -> dict:
    """
    Compare emissions for standard vs eco-certified hotels.
    Useful for showing potential savings.
    """
    from datetime import date, timedelta
    
    today = date.today()
    checkout = today + timedelta(days=nights)
    
    standard = calculate_hotel_emissions(
        country_code=country_code,
        check_in=today,
        check_out=checkout,
        star_rating=star_rating,
        sustainability_certified=False
    )
    
    eco = calculate_hotel_emissions(
        country_code=country_code,
        check_in=today,
        check_out=checkout,
        star_rating=star_rating,
        sustainability_certified=True
    )
    
    savings_kg = standard.emissions_kg - eco.emissions_kg
    savings_percent = (savings_kg / standard.emissions_kg) * 100 if standard.emissions_kg > 0 else 0
    
    return {
        "standard_emissions_kg": standard.emissions_kg,
        "eco_certified_emissions_kg": eco.emissions_kg,
        "savings_kg": round(savings_kg, 2),
        "savings_percent": round(savings_percent, 1)
    }
