"""
Emission factors endpoints.
"""

from flask import Blueprint, request, jsonify

from app.data.emission_factors import (
    FLIGHT_FACTORS_PER_KM,
    RADIATIVE_FORCING_MULTIPLIER,
    HOTEL_ENERGY_KWH_PER_NIGHT,
    TRAIN_FACTORS_PER_KM
)
from app.data.grid_intensity import get_grid_intensity, get_all_eu_intensities, GRID_INTENSITY
from app.data.airports import get_airport, calculate_distance_km, AIRPORTS

factors_bp = Blueprint("factors", __name__)


@factors_bp.route("/factors/flights", methods=["GET"])
def get_flight_factors():
    """
    Get current flight emission factors.
    
    Query params:
        - cabin_class: Filter by cabin class (optional)
        - haul_type: Filter by haul type (optional)
    """
    cabin_class = request.args.get("cabin_class")
    haul_type = request.args.get("haul_type")
    
    factors = []
    
    for haul, classes in FLIGHT_FACTORS_PER_KM.items():
        if haul_type and haul != haul_type:
            continue
        
        for cabin, factor in classes.items():
            if cabin_class and cabin != cabin_class:
                continue
            
            factors.append({
                "haul_type": haul,
                "cabin_class": cabin,
                "kg_co2e_per_km": round(factor, 4),
                "kg_co2e_per_km_with_rf": round(factor * RADIATIVE_FORCING_MULTIPLIER, 4),
                "radiative_forcing_multiplier": RADIATIVE_FORCING_MULTIPLIER
            })
    
    return jsonify({
        "factors": factors,
        "radiative_forcing_multiplier": RADIATIVE_FORCING_MULTIPLIER,
        "radiative_forcing_note": "Accounts for non-CO₂ effects at altitude (contrails, NOx)",
        "haul_type_definitions": {
            "short": "< 1,500 km",
            "medium": "1,500 - 4,000 km",
            "long": "> 4,000 km"
        },
        "cabin_class_multipliers": {
            "economy": 1.0,
            "premium_economy": 1.5,
            "business": 3.0,
            "first": 4.0
        },
        "source": "DEFRA 2024 + ICAO Carbon Calculator",
        "updated_at": "2024-12-01"
    }), 200


@factors_bp.route("/factors/hotels", methods=["GET"])
def get_hotel_factors():
    """
    Get hotel emission factors and grid intensity by region.
    
    Query params:
        - country_code: ISO 3166-1 alpha-2 country code (required)
    """
    country_code = request.args.get("country_code", "").upper()
    
    if not country_code:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "country_code query parameter is required"
        }), 400
    
    grid_data = get_grid_intensity(country_code)
    
    # Calculate emissions per night for each star rating
    hotel_factors = []
    for star, kwh in HOTEL_ENERGY_KWH_PER_NIGHT.items():
        emissions_kg = (kwh * grid_data["intensity"]) / 1000
        hotel_factors.append({
            "star_rating": star,
            "kwh_per_night": kwh,
            "kg_co2e_per_night": round(emissions_kg, 2)
        })
    
    return jsonify({
        "country_code": country_code,
        "grid_carbon_intensity": {
            "value_g_co2_per_kwh": grid_data["intensity"],
            "source": grid_data.get("source", "IEA"),
            "quality": grid_data.get("quality", "estimated"),
            "notes": grid_data.get("notes")
        },
        "hotel_emission_factors": hotel_factors,
        "eco_certification_discount": 0.35,
        "eco_certification_note": "Eco-certified hotels typically use 35% less energy",
        "source": "Cornell Hotel Sustainability Benchmarking Index + Grid data"
    }), 200


@factors_bp.route("/factors/trains", methods=["GET"])
def get_train_factors():
    """
    Get train emission factors by train type.
    """
    factors = []
    for train_type, factor in TRAIN_FACTORS_PER_KM.items():
        factors.append({
            "train_type": train_type,
            "kg_co2e_per_km": factor,
            "g_co2e_per_km": factor * 1000
        })
    
    # Sort by emissions (lowest first)
    factors.sort(key=lambda x: x["kg_co2e_per_km"])
    
    return jsonify({
        "factors": factors,
        "note": "Train emissions vary significantly based on energy source and occupancy",
        "source": "UIC Railway Handbook + Operator reports",
        "updated_at": "2024-12-01"
    }), 200


@factors_bp.route("/factors/grid-intensity", methods=["GET"])
def get_grid_intensities():
    """
    Get grid carbon intensities for multiple countries.
    
    Query params:
        - region: 'eu' for EU countries, 'all' for all available (default: all)
    """
    region = request.args.get("region", "all").lower()
    
    if region == "eu":
        intensities = get_all_eu_intensities()
    else:
        intensities = GRID_INTENSITY
    
    # Format response
    countries = []
    for code, data in intensities.items():
        countries.append({
            "country_code": code,
            "intensity_g_co2_per_kwh": data["intensity"],
            "source": data.get("source", "IEA"),
            "quality": data.get("quality", "estimated"),
            "notes": data.get("notes")
        })
    
    # Sort by intensity (lowest carbon first)
    countries.sort(key=lambda x: x["intensity_g_co2_per_kwh"])
    
    return jsonify({
        "region": region,
        "countries": countries,
        "total": len(countries),
        "lowest_carbon": countries[0]["country_code"] if countries else None,
        "highest_carbon": countries[-1]["country_code"] if countries else None
    }), 200


@factors_bp.route("/factors/airports", methods=["GET"])
def list_airports():
    """
    List supported airports.
    
    Query params:
        - country: Filter by country code (optional)
        - search: Search by city or airport name (optional)
    """
    country = request.args.get("country", "").upper()
    search = request.args.get("search", "").lower()
    
    airports = []
    for code, data in AIRPORTS.items():
        # Apply filters
        if country and data["country"] != country:
            continue
        if search and search not in data["name"].lower() and search not in data["city"].lower():
            continue
        
        airports.append({
            "code": code,
            "name": data["name"],
            "city": data["city"],
            "country": data["country"],
            "coordinates": {
                "latitude": data["lat"],
                "longitude": data["lon"]
            }
        })
    
    # Sort by code
    airports.sort(key=lambda x: x["code"])
    
    return jsonify({
        "airports": airports,
        "total": len(airports)
    }), 200


@factors_bp.route("/factors/distance", methods=["GET"])
def calculate_route_distance():
    """
    Calculate distance between two airports.
    
    Query params:
        - origin: Origin airport IATA code
        - destination: Destination airport IATA code
    """
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    
    if not origin or not destination:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "origin and destination query parameters required"
        }), 400
    
    origin_airport = get_airport(origin)
    dest_airport = get_airport(destination)
    
    if not origin_airport:
        return jsonify({
            "code": "NOT_FOUND",
            "message": f"Airport code '{origin}' not found"
        }), 404
    
    if not dest_airport:
        return jsonify({
            "code": "NOT_FOUND",
            "message": f"Airport code '{destination}' not found"
        }), 404
    
    distance = calculate_distance_km(origin, destination)
    
    # Determine haul type
    if distance < 1500:
        haul_type = "short"
    elif distance <= 4000:
        haul_type = "medium"
    else:
        haul_type = "long"
    
    return jsonify({
        "origin": {
            "code": origin,
            "name": origin_airport["name"],
            "city": origin_airport["city"],
            "country": origin_airport["country"]
        },
        "destination": {
            "code": destination,
            "name": dest_airport["name"],
            "city": dest_airport["city"],
            "country": dest_airport["country"]
        },
        "distance_km": distance,
        "haul_type": haul_type
    }), 200
