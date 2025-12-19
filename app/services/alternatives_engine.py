"""
Alternatives engine for finding lower-impact travel options.
"""

from typing import Optional
from dataclasses import dataclass

from app.data.airports import get_airport, calculate_distance_km
from app.data.emission_factors import get_train_factor, TRAIN_FACTORS_PER_KM
from app.services.flight_calculator import calculate_flight_emissions
from app.services.hotel_calculator import calculate_hotel_emissions


@dataclass
class TrainAlternative:
    """A train alternative to a flight."""
    route_name: str
    origin_station: str
    destination_station: str
    train_type: str
    emissions_kg: float
    distance_km: float
    duration_minutes: int
    estimated_cost_eur: float
    emission_factor: float
    available: bool


# Routes where train is a viable alternative to flight
# Format: (origin_airport, dest_airport): train_route_info
TRAIN_ROUTES: dict[tuple[str, str], dict] = {
    # UK - France via Eurostar
    ("LHR", "CDG"): {
        "train_type": "eurostar",
        "origin_station": "London St Pancras",
        "destination_station": "Paris Gare du Nord",
        "route_name": "Eurostar London → Paris",
        "distance_km": 459,
        "duration_minutes": 136,
        "typical_price_eur": 80
    },
    ("LGW", "CDG"): {
        "train_type": "eurostar",
        "origin_station": "London St Pancras",
        "destination_station": "Paris Gare du Nord",
        "route_name": "Eurostar London → Paris",
        "distance_km": 459,
        "duration_minutes": 136,
        "typical_price_eur": 80
    },
    ("STN", "CDG"): {
        "train_type": "eurostar",
        "origin_station": "London St Pancras",
        "destination_station": "Paris Gare du Nord",
        "route_name": "Eurostar London → Paris",
        "distance_km": 459,
        "duration_minutes": 136,
        "typical_price_eur": 80
    },
    
    # UK - Belgium via Eurostar
    ("LHR", "BRU"): {
        "train_type": "eurostar",
        "origin_station": "London St Pancras",
        "destination_station": "Brussels Midi",
        "route_name": "Eurostar London → Brussels",
        "distance_km": 373,
        "duration_minutes": 122,
        "typical_price_eur": 70
    },
    
    # UK - Netherlands via Eurostar
    ("LHR", "AMS"): {
        "train_type": "eurostar",
        "origin_station": "London St Pancras",
        "destination_station": "Amsterdam Centraal",
        "route_name": "Eurostar London → Amsterdam",
        "distance_km": 450,
        "duration_minutes": 229,
        "typical_price_eur": 85
    },
    
    # France - Belgium TGV
    ("CDG", "BRU"): {
        "train_type": "tgv",
        "origin_station": "Paris Gare du Nord",
        "destination_station": "Brussels Midi",
        "route_name": "Thalys Paris → Brussels",
        "distance_km": 306,
        "duration_minutes": 82,
        "typical_price_eur": 45
    },
    
    # France - Germany TGV/ICE
    ("CDG", "FRA"): {
        "train_type": "ice",
        "origin_station": "Paris Est",
        "destination_station": "Frankfurt Hbf",
        "route_name": "ICE/TGV Paris → Frankfurt",
        "distance_km": 479,
        "duration_minutes": 232,
        "typical_price_eur": 60
    },
    
    # Germany internal - ICE
    ("FRA", "MUC"): {
        "train_type": "ice",
        "origin_station": "Frankfurt Hbf",
        "destination_station": "München Hbf",
        "route_name": "ICE Frankfurt → Munich",
        "distance_km": 304,
        "duration_minutes": 195,
        "typical_price_eur": 50
    },
    ("FRA", "BER"): {
        "train_type": "ice",
        "origin_station": "Frankfurt Hbf",
        "destination_station": "Berlin Hbf",
        "route_name": "ICE Frankfurt → Berlin",
        "distance_km": 423,
        "duration_minutes": 240,
        "typical_price_eur": 55
    },
    
    # Germany - Italy
    ("FRA", "MXP"): {
        "train_type": "ice",
        "origin_station": "Frankfurt Hbf",
        "destination_station": "Milano Centrale",
        "route_name": "EC Frankfurt → Milan",
        "distance_km": 520,
        "duration_minutes": 480,
        "typical_price_eur": 70
    },
    
    # France - Spain
    ("CDG", "BCN"): {
        "train_type": "tgv",
        "origin_station": "Paris Lyon",
        "destination_station": "Barcelona Sants",
        "route_name": "TGV Paris → Barcelona",
        "distance_km": 830,
        "duration_minutes": 382,
        "typical_price_eur": 90
    },
    
    # Italy internal
    ("FCO", "MXP"): {
        "train_type": "eu_high_speed",
        "origin_station": "Roma Termini",
        "destination_station": "Milano Centrale",
        "route_name": "Frecciarossa Rome → Milan",
        "distance_km": 476,
        "duration_minutes": 175,
        "typical_price_eur": 55
    },
    
    # Spain internal
    ("MAD", "BCN"): {
        "train_type": "eu_high_speed",
        "origin_station": "Madrid Atocha",
        "destination_station": "Barcelona Sants",
        "route_name": "AVE Madrid → Barcelona",
        "distance_km": 505,
        "duration_minutes": 155,
        "typical_price_eur": 50
    },
}


def find_train_alternative(origin: str, destination: str) -> Optional[TrainAlternative]:
    """
    Find a train alternative for a flight route.
    
    Args:
        origin: Origin airport IATA code
        destination: Destination airport IATA code
    
    Returns:
        TrainAlternative if a route exists, None otherwise
    """
    origin = origin.upper()
    destination = destination.upper()
    
    # Check both directions
    route_key = (origin, destination)
    reverse_key = (destination, origin)
    
    route_info = TRAIN_ROUTES.get(route_key) or TRAIN_ROUTES.get(reverse_key)
    
    if not route_info:
        return None
    
    # Calculate emissions
    train_type = route_info["train_type"]
    distance_km = route_info["distance_km"]
    emission_factor = get_train_factor(train_type)
    emissions_kg = distance_km * emission_factor
    
    return TrainAlternative(
        route_name=route_info["route_name"],
        origin_station=route_info["origin_station"],
        destination_station=route_info["destination_station"],
        train_type=train_type,
        emissions_kg=round(emissions_kg, 2),
        distance_km=distance_km,
        duration_minutes=route_info["duration_minutes"],
        estimated_cost_eur=route_info["typical_price_eur"],
        emission_factor=emission_factor,
        available=True
    )


def generate_alternatives(
    segments: list[dict],
    max_alternatives: int = 3
) -> list[dict]:
    """
    Generate lower-impact alternatives for an itinerary.
    
    Args:
        segments: List of segment dictionaries from the request
        max_alternatives: Maximum number of alternatives to return
    
    Returns:
        List of alternative itineraries with savings calculations
    """
    alternatives = []
    
    # Analyze each segment for potential improvements
    flight_segments = [s for s in segments if s.get("type") == "flight"]
    hotel_segments = [s for s in segments if s.get("type") == "hotel"]
    
    # Strategy 1: Replace flights with trains where possible
    train_alternative = _generate_train_alternative(segments, flight_segments)
    if train_alternative:
        alternatives.append(train_alternative)
    
    # Strategy 2: Switch to eco-certified hotels
    eco_hotel_alternative = _generate_eco_hotel_alternative(segments, hotel_segments)
    if eco_hotel_alternative:
        alternatives.append(eco_hotel_alternative)
    
    # Strategy 3: Combined (train + eco hotel)
    if train_alternative and eco_hotel_alternative:
        combined = _generate_combined_alternative(segments, flight_segments, hotel_segments)
        if combined:
            alternatives.append(combined)
    
    # Sort by savings percentage
    alternatives.sort(key=lambda x: x.get("savings", {}).get("percentage", 0), reverse=True)
    
    return alternatives[:max_alternatives]


def _generate_train_alternative(segments: list[dict], flight_segments: list[dict]) -> Optional[dict]:
    """Generate an alternative that replaces flights with trains."""
    from datetime import date
    
    if not flight_segments:
        return None
    
    modified_segments = []
    total_original_emissions = 0
    total_new_emissions = 0
    has_train_replacement = False
    
    for i, seg in enumerate(segments):
        if seg.get("type") == "flight":
            origin = seg.get("origin", "")
            dest = seg.get("destination", "")
            
            # Calculate original flight emissions
            flight_result = calculate_flight_emissions(
                origin=origin,
                destination=dest,
                cabin_class=seg.get("cabin_class", "economy")
            )
            
            if flight_result:
                total_original_emissions += flight_result.emissions_kg
            
            # Check for train alternative
            train_alt = find_train_alternative(origin, dest)
            
            if train_alt:
                has_train_replacement = True
                total_new_emissions += train_alt.emissions_kg
                modified_segments.append({
                    "type": "train",
                    "original_segment_index": i,
                    "description": train_alt.route_name,
                    "emissions_kg": train_alt.emissions_kg,
                    "details": {
                        "origin_station": train_alt.origin_station,
                        "destination_station": train_alt.destination_station,
                        "duration_minutes": train_alt.duration_minutes,
                        "train_type": train_alt.train_type,
                        "emission_factor_kg_per_km": train_alt.emission_factor
                    }
                })
            else:
                # Keep original flight
                if flight_result:
                    total_new_emissions += flight_result.emissions_kg
                modified_segments.append({
                    "type": "flight",
                    "original_segment_index": i,
                    "description": f"Same flight {origin} → {dest}",
                    "emissions_kg": flight_result.emissions_kg if flight_result else 0
                })
        else:
            # Keep other segments (hotels, etc.)
            # For now, just estimate hotel emissions
            modified_segments.append({
                "type": seg.get("type"),
                "original_segment_index": i,
                "description": "Same as original",
                "emissions_kg": 0  # Would need to calculate
            })
    
    if not has_train_replacement:
        return None
    
    savings_kg = total_original_emissions - total_new_emissions
    savings_percent = (savings_kg / total_original_emissions * 100) if total_original_emissions > 0 else 0
    
    return {
        "alternative_id": "alt_train",
        "total_emissions": {
            "co2e_kg": round(total_new_emissions, 2),
            "unit": "kg_co2e"
        },
        "savings": {
            "absolute_kg": round(savings_kg, 2),
            "percentage": round(savings_percent, 1),
            "label": f"Saves {round(savings_kg, 1)} kg CO₂e ({round(savings_percent)}% reduction)"
        },
        "segments": modified_segments,
        "tradeoffs": {
            "time_difference_minutes": 60,  # Approximate
            "estimated_cost_difference_eur": -30,  # Trains often cheaper
            "comfort_score": 4.5
        },
        "recommendation_reason": "Taking the train instead of flying significantly reduces emissions with minimal journey time difference."
    }


def _generate_eco_hotel_alternative(segments: list[dict], hotel_segments: list[dict]) -> Optional[dict]:
    """Generate an alternative using eco-certified hotels."""
    from datetime import datetime
    
    if not hotel_segments:
        return None
    
    modified_segments = []
    total_savings_kg = 0
    original_hotel_emissions = 0
    new_hotel_emissions = 0
    
    for i, seg in enumerate(segments):
        if seg.get("type") == "hotel":
            location = seg.get("location", {})
            country_code = location.get("country_code", "GB")
            
            check_in_str = seg.get("check_in", "")
            check_out_str = seg.get("check_out", "")
            
            try:
                check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
            except:
                from datetime import date, timedelta
                check_in = date.today()
                check_out = check_in + timedelta(days=2)
            
            star_rating = seg.get("star_rating", 4)
            
            # Calculate original emissions
            original = calculate_hotel_emissions(
                country_code=country_code,
                check_in=check_in,
                check_out=check_out,
                star_rating=star_rating,
                sustainability_certified=False
            )
            original_hotel_emissions += original.emissions_kg
            
            # Calculate eco-certified emissions
            eco = calculate_hotel_emissions(
                country_code=country_code,
                check_in=check_in,
                check_out=check_out,
                star_rating=star_rating,
                sustainability_certified=True
            )
            new_hotel_emissions += eco.emissions_kg
            
            segment_savings = original.emissions_kg - eco.emissions_kg
            total_savings_kg += segment_savings
            
            modified_segments.append({
                "type": "hotel",
                "original_segment_index": i,
                "description": f"Eco-certified {star_rating}-star hotel, {location.get('city', 'Same location')}",
                "emissions_kg": eco.emissions_kg,
                "details": {
                    "sustainability_certified": True,
                    "energy_reduction_percent": 35,
                    "certification": "EU Ecolabel / Green Key"
                }
            })
        else:
            modified_segments.append({
                "type": seg.get("type"),
                "original_segment_index": i,
                "description": "Same as original",
                "emissions_kg": 0
            })
    
    if total_savings_kg <= 0:
        return None
    
    savings_percent = (total_savings_kg / original_hotel_emissions * 100) if original_hotel_emissions > 0 else 0
    
    return {
        "alternative_id": "alt_eco_hotel",
        "total_emissions": {
            "co2e_kg": round(new_hotel_emissions, 2),
            "unit": "kg_co2e"
        },
        "savings": {
            "absolute_kg": round(total_savings_kg, 2),
            "percentage": round(savings_percent, 1),
            "label": f"Saves {round(total_savings_kg, 1)} kg CO₂e ({round(savings_percent)}% reduction on hotels)"
        },
        "segments": modified_segments,
        "tradeoffs": {
            "time_difference_minutes": 0,
            "estimated_cost_difference_eur": -20,  # Often similar or cheaper
            "comfort_score": 4.0
        },
        "recommendation_reason": "Switching to an eco-certified hotel reduces accommodation emissions without compromising comfort."
    }


def _generate_combined_alternative(
    segments: list[dict], 
    flight_segments: list[dict],
    hotel_segments: list[dict]
) -> Optional[dict]:
    """Generate a combined train + eco-hotel alternative."""
    train_alt = _generate_train_alternative(segments, flight_segments)
    eco_alt = _generate_eco_hotel_alternative(segments, hotel_segments)
    
    if not train_alt or not eco_alt:
        return None
    
    combined_emissions = (
        train_alt["total_emissions"]["co2e_kg"] + 
        eco_alt["total_emissions"]["co2e_kg"]
    )
    
    combined_savings = (
        train_alt["savings"]["absolute_kg"] + 
        eco_alt["savings"]["absolute_kg"]
    )
    
    return {
        "alternative_id": "alt_combined",
        "total_emissions": {
            "co2e_kg": round(combined_emissions, 2),
            "unit": "kg_co2e"
        },
        "savings": {
            "absolute_kg": round(combined_savings, 2),
            "percentage": 0,  # Would need total original to calculate
            "label": f"Saves {round(combined_savings, 1)} kg CO₂e (combined improvements)"
        },
        "segments": train_alt["segments"],  # Simplified
        "tradeoffs": {
            "time_difference_minutes": 60,
            "estimated_cost_difference_eur": -50,
            "comfort_score": 4.3
        },
        "recommendation_reason": "Best overall: Combining train travel with eco-hotels achieves maximum emission reduction."
    }
