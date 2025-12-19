"""
Carbon assessment endpoints.
"""

import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app

from app.services.flight_calculator import calculate_flight_emissions
from app.services.hotel_calculator import calculate_hotel_emissions
from app.services.alternatives_engine import generate_alternatives
from app.services.confidence_scorer import calculate_confidence_score, aggregate_confidence_factors
from app.data.emission_factors import calculate_equivalents
from app.data.transport_factors import (
    calculate_transfer_emissions,
    calculate_city_transport_emissions,
    CAR_FACTORS_PER_KM
)

assess_bp = Blueprint("assess", __name__)


def validate_request(data: dict) -> tuple[bool, str]:
    """Validate assessment request."""
    if not data:
        return False, "Request body is required"
    
    segments = data.get("segments")
    if not segments or not isinstance(segments, list):
        return False, "segments array is required"
    
    if len(segments) == 0:
        return False, "At least one segment is required"
    
    if len(segments) > 50:
        return False, "Maximum 50 segments allowed"
    
    for i, seg in enumerate(segments):
        seg_type = seg.get("type")
        if seg_type not in ["flight", "hotel", "transfer", "taxi", "transport"]:
            return False, f"segments[{i}].type must be 'flight', 'hotel', 'transfer', 'taxi', or 'transport'"
        
        if seg_type == "flight":
            if not seg.get("origin"):
                return False, f"segments[{i}].origin is required for flights"
            if not seg.get("destination"):
                return False, f"segments[{i}].destination is required for flights"
            if not seg.get("departure_date"):
                return False, f"segments[{i}].departure_date is required for flights"
        
        if seg_type == "hotel":
            if not seg.get("location"):
                return False, f"segments[{i}].location is required for hotels"
            if not seg.get("location", {}).get("country_code"):
                return False, f"segments[{i}].location.country_code is required"
            if not seg.get("check_in"):
                return False, f"segments[{i}].check_in is required for hotels"
            if not seg.get("check_out"):
                return False, f"segments[{i}].check_out is required for hotels"
    
    return True, ""


@assess_bp.route("/assess", methods=["POST"])
def assess_itinerary():
    """
    Calculate carbon emissions for a travel itinerary.
    
    Request body:
        - trip_id: Optional client identifier
        - traveler_count: Number of travelers (default 1)
        - segments: Array of flight/hotel segments
        - options: Assessment options
    
    Returns:
        Assessment with total emissions, confidence score, and alternatives
    """
    data = request.get_json()
    
    # Validate request
    valid, error_msg = validate_request(data)
    if not valid:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": error_msg
        }), 400
    
    try:
        result = process_assessment(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({
            "code": "PROCESSING_ERROR",
            "message": str(e)
        }), 422
    except Exception as e:
        current_app.logger.error(f"Assessment error: {e}")
        return jsonify({
            "code": "INTERNAL_ERROR",
            "message": "An error occurred processing your request"
        }), 500


def process_assessment(data: dict) -> dict:
    """Process an assessment request and return results."""
    trip_id = data.get("trip_id")
    traveler_count = data.get("traveler_count", 1)
    segments = data.get("segments", [])
    options = data.get("options", {})
    
    # Track totals
    total_flights_kg = 0.0
    total_hotels_kg = 0.0
    total_transport_kg = 0.0
    segment_results = []
    all_confidence_factors = []
    grid_data_quality = "default"
    haul_types = []
    
    # Process each segment
    for i, seg in enumerate(segments):
        seg_type = seg.get("type")
        
        if seg_type == "flight":
            result = process_flight_segment(seg, i)
            if result:
                emissions = result["emissions_kg"] * traveler_count
                total_flights_kg += emissions
                result["emissions_kg"] = round(emissions, 2)
                segment_results.append(result)
                all_confidence_factors.extend(result.get("_confidence_factors", []))
                if result.get("details", {}).get("haul_type"):
                    haul_types.append(result["details"]["haul_type"])
        
        elif seg_type == "hotel":
            result = process_hotel_segment(seg, i, traveler_count)
            if result:
                total_hotels_kg += result["emissions_kg"]
                segment_results.append(result)
                all_confidence_factors.extend(result.get("_confidence_factors", []))
                # Track grid quality
                quality = result.get("_grid_quality", "default")
                if quality == "measured":
                    grid_data_quality = "measured"
                elif quality == "estimated" and grid_data_quality == "default":
                    grid_data_quality = "estimated"
        
        elif seg_type in ["transfer", "taxi", "transport"]:
            result = process_transport_segment(seg, i, traveler_count)
            if result:
                total_transport_kg += result["emissions_kg"]
                segment_results.append(result)
                all_confidence_factors.extend(result.get("_confidence_factors", []))
    
    # Calculate totals
    total_emissions_kg = total_flights_kg + total_hotels_kg + total_transport_kg
    
    # Calculate confidence score
    primary_haul = haul_types[0] if haul_types else None
    confidence = calculate_confidence_score(
        factors=all_confidence_factors,
        has_carrier_data=any(seg.get("carrier_code") for seg in segments if seg.get("type") == "flight"),
        grid_data_quality=grid_data_quality,
        haul_type=primary_haul
    )
    
    # Build response
    response = {
        "assessment_id": f"assess_{uuid.uuid4()}",
        "trip_id": trip_id,
        "total_emissions": {
            "co2e_kg": round(total_emissions_kg, 2),
            "unit": "kg_co2e",
            "breakdown": {
                "flights_kg": round(total_flights_kg, 2),
                "hotels_kg": round(total_hotels_kg, 2),
                "transport_kg": round(total_transport_kg, 2)
            },
            "per_traveler_kg": round(total_emissions_kg / traveler_count, 2),
            "equivalent": calculate_equivalents(total_emissions_kg)
        },
        "confidence_score": confidence,
        "segments": [
            {k: v for k, v in seg.items() if not k.startswith("_")}
            for seg in segment_results
        ],
        "created_at": datetime.utcnow().isoformat() + "Z",
        "expires_at": (datetime.utcnow() + timedelta(days=90)).isoformat() + "Z"
    }
    
    # Include alternatives if requested
    if options.get("include_alternatives", False):
        alt_count = options.get("alternative_count", 3)
        alternatives = generate_alternatives(segments, max_alternatives=alt_count)
        if alternatives:
            # Calculate savings percentages
            for alt in alternatives:
                if alt.get("savings", {}).get("absolute_kg"):
                    savings_pct = (alt["savings"]["absolute_kg"] / total_emissions_kg * 100) if total_emissions_kg > 0 else 0
                    alt["savings"]["percentage"] = round(savings_pct, 1)
                    alt["savings"]["label"] = f"Saves {alt['savings']['absolute_kg']} kg CO₂e ({round(savings_pct)}% reduction)"
            response["lower_impact_alternatives"] = alternatives
    
    # Include methodology if requested
    if options.get("include_methodology", False):
        response["methodology"] = {
            "standards": [
                "ICAO Carbon Emissions Calculator Methodology (v12)",
                "GHG Protocol Scope 3 Category 6",
                "DEFRA Greenhouse Gas Reporting Conversion Factors 2024"
            ],
            "calculation_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "emission_factors_version": "2024.2",
            "notes": [
                "Flight emissions include radiative forcing multiplier of 1.9 for high-altitude effects",
                "Hotel emissions calculated using regional grid carbon intensity data",
                "Cabin class allocation based on floor space methodology"
            ]
        }
    
    return response


def process_flight_segment(seg: dict, index: int) -> dict:
    """Process a flight segment and return emission details."""
    origin = seg.get("origin", "").upper()
    destination = seg.get("destination", "").upper()
    cabin_class = seg.get("cabin_class", "economy")
    carrier_code = seg.get("carrier_code")
    
    result = calculate_flight_emissions(
        origin=origin,
        destination=destination,
        cabin_class=cabin_class,
        carrier_code=carrier_code
    )
    
    if not result:
        raise ValueError(f"Could not calculate emissions for route {origin} → {destination}")
    
    return {
        "segment_index": index,
        "type": "flight",
        "emissions_kg": result.emissions_kg,
        "details": {
            "distance_km": result.distance_km,
            "haul_type": result.haul_type,
            "radiative_forcing_multiplier": result.radiative_forcing_multiplier,
            "fuel_burn_kg": result.fuel_burn_kg,
            "aircraft_type": result.aircraft_type,
            "load_factor": result.load_factor,
            "emission_factor_source": result.emission_factor_source
        },
        "_confidence_factors": result.confidence_factors
    }


def process_hotel_segment(seg: dict, index: int, traveler_count: int = 1) -> dict:
    """Process a hotel segment and return emission details."""
    from datetime import datetime as dt
    
    location = seg.get("location", {})
    country_code = location.get("country_code", "GB").upper()
    
    check_in_str = seg.get("check_in", "")
    check_out_str = seg.get("check_out", "")
    
    try:
        check_in = dt.strptime(check_in_str, "%Y-%m-%d").date()
        check_out = dt.strptime(check_out_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format for hotel segment {index}")
    
    star_rating = seg.get("star_rating", 4)
    room_count = seg.get("room_count", 1)
    persons = seg.get("persons", traveler_count)
    sustainability_certified = seg.get("sustainability_certified", False)
    breakfast_type = seg.get("breakfast", "none")
    
    result = calculate_hotel_emissions(
        country_code=country_code,
        check_in=check_in,
        check_out=check_out,
        star_rating=star_rating,
        room_count=room_count,
        persons=persons,
        sustainability_certified=sustainability_certified,
        breakfast_type=breakfast_type
    )
    
    details = {
        "nights": result.nights,
        "rooms": result.rooms,
        "persons": result.persons,
        "emissions_per_night_kg": result.emissions_per_night_kg,
        "grid_carbon_intensity": result.grid_carbon_intensity,
        "energy_consumption_kwh": result.energy_consumption_kwh,
        "emission_factor_source": result.emission_factor_source
    }
    
    # Add breakfast info if included
    if breakfast_type != "none":
        details["breakfast"] = {
            "type": result.breakfast_type,
            "emissions_kg": result.breakfast_emissions_kg
        }
    
    return {
        "segment_index": index,
        "type": "hotel",
        "emissions_kg": result.emissions_kg,
        "details": details,
        "_confidence_factors": result.confidence_factors,
        "_grid_quality": result.grid_carbon_intensity.get("source", "").lower()
    }


def process_transport_segment(seg: dict, index: int, traveler_count: int = 1) -> dict:
    """Process a ground transport segment (taxi, Uber, transfer)."""
    transport_type = seg.get("type", "taxi")
    vehicle_type = seg.get("vehicle_type", "uber_x")
    
    if transport_type == "transfer":
        # Airport transfer
        airport_code = seg.get("airport", "")
        is_round_trip = seg.get("round_trip", True)
        
        result = calculate_transfer_emissions(
            airport_code=airport_code,
            vehicle_type=vehicle_type,
            is_round_trip=is_round_trip
        )
        
        # Multiply by number of travelers if sharing not specified
        if not seg.get("shared", False):
            result["emissions_kg"] = round(result["emissions_kg"] * traveler_count, 2)
        
        return {
            "segment_index": index,
            "type": "transfer",
            "emissions_kg": result["emissions_kg"],
            "details": {
                "airport": airport_code,
                "city": result["city"],
                "distance_km": result["distance_km"],
                "vehicle_type": result["vehicle_type"],
                "round_trip": is_round_trip,
                "factor_per_km": result["factor_per_km"],
                "emission_factor_source": "DEFRA 2024"
            },
            "_confidence_factors": [{
                "factor": "ground_transport",
                "impact": "positive",
                "description": "Using DEFRA 2024 vehicle emission factors"
            }]
        }
    
    else:
        # City transport (taxi, Uber by km)
        distance_km = seg.get("distance_km", 10)
        
        result = calculate_city_transport_emissions(
            distance_km=distance_km,
            vehicle_type=vehicle_type
        )
        
        return {
            "segment_index": index,
            "type": "transport",
            "emissions_kg": result["emissions_kg"],
            "details": {
                "distance_km": result["distance_km"],
                "vehicle_type": result["vehicle_type"],
                "factor_per_km": result["factor_per_km"],
                "emission_factor_source": "DEFRA 2024"
            },
            "_confidence_factors": [{
                "factor": "ground_transport",
                "impact": "positive",
                "description": "Using DEFRA 2024 vehicle emission factors"
            }]
        }


@assess_bp.route("/assess/batch", methods=["POST"])
def batch_assess():
    """
    Batch assess multiple itineraries.
    
    Request body:
        - batch_id: Optional client identifier
        - itineraries: Array of itinerary requests (max 100)
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"code": "VALIDATION_ERROR", "message": "Request body required"}), 400
    
    itineraries = data.get("itineraries", [])
    if not itineraries:
        return jsonify({"code": "VALIDATION_ERROR", "message": "itineraries array required"}), 400
    
    if len(itineraries) > 100:
        return jsonify({"code": "VALIDATION_ERROR", "message": "Maximum 100 itineraries allowed"}), 400
    
    results = []
    successful = 0
    failed = 0
    total_emissions = 0.0
    
    for itin in itineraries:
        try:
            valid, error = validate_request(itin)
            if not valid:
                results.append({
                    "trip_id": itin.get("trip_id"),
                    "status": "error",
                    "error": {"code": "VALIDATION_ERROR", "message": error}
                })
                failed += 1
                continue
            
            assessment = process_assessment(itin)
            results.append({
                "trip_id": itin.get("trip_id"),
                "status": "success",
                "assessment": assessment
            })
            successful += 1
            total_emissions += assessment["total_emissions"]["co2e_kg"]
        except Exception as e:
            results.append({
                "trip_id": itin.get("trip_id"),
                "status": "error",
                "error": {"code": "PROCESSING_ERROR", "message": str(e)}
            })
            failed += 1
    
    return jsonify({
        "batch_id": data.get("batch_id", f"batch_{uuid.uuid4()}"),
        "total_itineraries": len(itineraries),
        "successful": successful,
        "failed": failed,
        "results": results,
        "aggregate": {
            "total_emissions_kg": round(total_emissions, 2),
            "average_per_trip_kg": round(total_emissions / successful, 2) if successful > 0 else 0
        }
    }), 200
