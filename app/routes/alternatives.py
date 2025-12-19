"""
Alternatives endpoint for finding lower-impact travel options.
"""

import uuid
from flask import Blueprint, request, jsonify

from app.services.flight_calculator import calculate_flight_emissions
from app.services.hotel_calculator import calculate_hotel_emissions
from app.services.alternatives_engine import generate_alternatives, find_train_alternative
from app.data.emission_factors import calculate_equivalents

alternatives_bp = Blueprint("alternatives", __name__)


@alternatives_bp.route("/alternatives", methods=["POST"])
def find_alternatives():
    """
    Find lower-impact alternatives for a travel itinerary.
    
    Request body:
        - segments: Array of flight/hotel segments
        - constraints: Optional constraints on alternatives
        - ranking_preference: emissions, cost, time, or balanced
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "Request body is required"
        }), 400
    
    segments = data.get("segments", [])
    if not segments:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "segments array is required"
        }), 400
    
    try:
        # Calculate original emissions
        original_emissions = calculate_original_emissions(segments)
        
        # Generate alternatives
        constraints = data.get("constraints", {})
        ranking = data.get("ranking_preference", "emissions")
        max_alternatives = constraints.get("max_alternatives", 5)
        
        alternatives = generate_alternatives(segments, max_alternatives=max_alternatives)
        
        # Update alternatives with proper savings percentages
        for alt in alternatives:
            if alt.get("savings"):
                savings_kg = alt["savings"]["absolute_kg"]
                pct = (savings_kg / original_emissions["co2e_kg"] * 100) if original_emissions["co2e_kg"] > 0 else 0
                alt["savings"]["percentage"] = round(pct, 1)
                alt["savings"]["label"] = f"Saves {savings_kg} kg CO₂e ({round(pct)}% reduction)"
        
        # Sort by preference
        if ranking == "emissions":
            alternatives.sort(key=lambda x: x.get("total_emissions", {}).get("co2e_kg", float("inf")))
        elif ranking == "time":
            alternatives.sort(key=lambda x: x.get("tradeoffs", {}).get("time_difference_minutes", 0))
        elif ranking == "cost":
            alternatives.sort(key=lambda x: x.get("tradeoffs", {}).get("estimated_cost_difference_eur", 0))
        
        # Build response
        best_summary = ""
        if alternatives:
            best = alternatives[0]
            savings = best.get("savings", {})
            best_summary = f"Best option saves {savings.get('absolute_kg', 0)} kg CO₂e ({savings.get('percentage', 0)}% reduction)"
        
        return jsonify({
            "original_emissions": original_emissions,
            "alternatives": alternatives,
            "best_alternative_summary": best_summary
        }), 200
    
    except ValueError as e:
        return jsonify({
            "code": "PROCESSING_ERROR",
            "message": str(e)
        }), 422
    except Exception as e:
        return jsonify({
            "code": "INTERNAL_ERROR",
            "message": "An error occurred processing your request"
        }), 500


def calculate_original_emissions(segments: list) -> dict:
    """Calculate total emissions for the original itinerary."""
    from datetime import datetime as dt
    
    total_flights = 0.0
    total_hotels = 0.0
    
    for seg in segments:
        seg_type = seg.get("type")
        
        if seg_type == "flight":
            result = calculate_flight_emissions(
                origin=seg.get("origin", "").upper(),
                destination=seg.get("destination", "").upper(),
                cabin_class=seg.get("cabin_class", "economy")
            )
            if result:
                total_flights += result.emissions_kg
        
        elif seg_type == "hotel":
            location = seg.get("location", {})
            country_code = location.get("country_code", "GB")
            
            try:
                check_in = dt.strptime(seg.get("check_in", ""), "%Y-%m-%d").date()
                check_out = dt.strptime(seg.get("check_out", ""), "%Y-%m-%d").date()
            except:
                from datetime import date, timedelta
                check_in = date.today()
                check_out = check_in + timedelta(days=2)
            
            result = calculate_hotel_emissions(
                country_code=country_code,
                check_in=check_in,
                check_out=check_out,
                star_rating=seg.get("star_rating", 4),
                room_count=seg.get("room_count", 1),
                sustainability_certified=seg.get("sustainability_certified", False)
            )
            total_hotels += result.emissions_kg
    
    total = total_flights + total_hotels
    
    return {
        "co2e_kg": round(total, 2),
        "unit": "kg_co2e",
        "breakdown": {
            "flights_kg": round(total_flights, 2),
            "hotels_kg": round(total_hotels, 2)
        },
        "equivalent": calculate_equivalents(total)
    }


@alternatives_bp.route("/alternatives/train-routes", methods=["GET"])
def list_train_routes():
    """
    List available train routes that can substitute flights.
    """
    from app.services.alternatives_engine import TRAIN_ROUTES
    
    routes = []
    for (origin, dest), info in TRAIN_ROUTES.items():
        routes.append({
            "origin_airport": origin,
            "destination_airport": dest,
            "train_type": info["train_type"],
            "route_name": info["route_name"],
            "duration_minutes": info["duration_minutes"],
            "distance_km": info["distance_km"],
            "typical_price_eur": info["typical_price_eur"]
        })
    
    return jsonify({
        "available_routes": routes,
        "total": len(routes)
    }), 200


@alternatives_bp.route("/alternatives/check-train", methods=["GET"])
def check_train_route():
    """
    Check if a train alternative exists for a specific route.
    
    Query params:
        - origin: Origin airport code
        - destination: Destination airport code
    """
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    
    if not origin or not destination:
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "origin and destination query parameters required"
        }), 400
    
    train = find_train_alternative(origin, destination)
    
    if train:
        # Also calculate flight emissions for comparison
        flight = calculate_flight_emissions(origin, destination)
        
        return jsonify({
            "train_available": True,
            "route": {
                "origin_airport": origin,
                "destination_airport": destination,
                "train_route": train.route_name,
                "origin_station": train.origin_station,
                "destination_station": train.destination_station,
                "train_type": train.train_type,
                "duration_minutes": train.duration_minutes,
                "distance_km": train.distance_km,
                "emissions_kg": train.emissions_kg,
                "estimated_cost_eur": train.estimated_cost_eur
            },
            "comparison": {
                "flight_emissions_kg": flight.emissions_kg if flight else None,
                "train_emissions_kg": train.emissions_kg,
                "savings_kg": round(flight.emissions_kg - train.emissions_kg, 2) if flight else None,
                "savings_percent": round((1 - train.emissions_kg / flight.emissions_kg) * 100, 1) if flight else None
            } if flight else None
        }), 200
    else:
        return jsonify({
            "train_available": False,
            "message": f"No direct train route available for {origin} → {destination}"
        }), 200
