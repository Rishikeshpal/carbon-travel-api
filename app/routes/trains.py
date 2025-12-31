"""
Train routes API endpoints.
Provides European train schedules, journey times, and carbon comparison.
"""

from flask import Blueprint, request, jsonify
from app.services.train_service import (
    search_train_journeys,
    compare_train_vs_flight,
    get_train_route,
    get_booking_links,
    TRAIN_ROUTES,
    TRAIN_STATIONS,
    BOOKING_PLATFORMS,
    format_duration
)
from app.services.flight_calculator import calculate_flight_emissions
from app.data.airports import calculate_distance_km

bp = Blueprint("trains", __name__, url_prefix="/v1/trains")


@bp.route("/search", methods=["GET"])
def search_trains():
    """
    Search for train journeys between two points.
    
    Query params:
        origin: Origin airport code (e.g., LHR)
        destination: Destination airport code (e.g., CDG)
        date: Optional travel date (YYYY-MM-DD)
    """
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    date = request.args.get("date")
    
    if not origin or not destination:
        return jsonify({
            "error": "Missing required parameters",
            "required": ["origin", "destination"]
        }), 400
    
    result = search_train_journeys(origin, destination, date)
    return jsonify(result)


@bp.route("/compare", methods=["GET"])
def compare_with_flight():
    """
    Compare train vs flight for a route.
    Shows emissions, duration, and journey details.
    
    Query params:
        origin: Origin airport code
        destination: Destination airport code
        cabin_class: Flight cabin class (economy, business, first)
    """
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    cabin_class = request.args.get("cabin_class", "economy").lower()
    
    if not origin or not destination:
        return jsonify({
            "error": "Missing required parameters",
            "required": ["origin", "destination"]
        }), 400
    
    # Calculate flight emissions
    try:
        flight_result = calculate_flight_emissions(
            origin=origin,
            destination=destination,
            cabin_class=cabin_class
        )
        flight_emissions = flight_result.emissions_kg
        flight_distance = flight_result.distance_km
        # Estimate flight duration: ~800 km/h average + 30 min for takeoff/landing
        flight_duration = int((flight_distance / 800) * 60) + 30
    except Exception as e:
        return jsonify({
            "error": f"Could not calculate flight emissions: {str(e)}"
        }), 400
    
    # Get train comparison
    train_data = search_train_journeys(origin, destination)
    
    if not train_data["found"]:
        return jsonify({
            "route": {
                "origin": origin,
                "destination": destination
            },
            "train_available": False,
            "message": train_data["message"],
            "flight": {
                "emissions_kg": round(flight_emissions, 1),
                "distance_km": round(flight_distance, 0),
                "duration_minutes": flight_duration,
                "cabin_class": cabin_class
            }
        })
    
    train_emissions = train_data["emissions"]["co2_kg"]
    savings_kg = flight_emissions - train_emissions
    savings_percent = (savings_kg / flight_emissions) * 100 if flight_emissions > 0 else 0
    
    # Get booking links
    date = request.args.get("date")
    booking_links = get_booking_links(origin, destination, date)
    
    return jsonify({
        "route": {
            "origin": origin,
            "destination": destination,
            "origin_city": train_data["route"]["origin"]["city"],
            "destination_city": train_data["route"]["destination"]["city"]
        },
        "train_available": True,
        "comparison": {
            "emissions": {
                "flight_kg": round(flight_emissions, 1),
                "train_kg": round(train_emissions, 1),
                "savings_kg": round(savings_kg, 1),
                "savings_percent": round(savings_percent, 0),
                "train_is_greener": savings_kg > 0
            },
            "duration": {
                "flight_minutes": flight_duration,
                "train_minutes": train_data["journey"]["duration_minutes"],
                "difference_minutes": train_data["journey"]["duration_minutes"] - flight_duration
            },
            "distance": {
                "flight_km": round(flight_distance, 0),
                "train_km": train_data["journey"]["distance_km"]
            }
        },
        "train": {
            "operator": train_data["journey"]["operator"],
            "duration": train_data["journey"]["duration"],
            "high_speed": train_data["journey"]["high_speed"],
            "stations": train_data["stations"],
            "schedule": train_data["schedule"],
            "origin_station": train_data["route"]["origin"]["station"],
            "destination_station": train_data["route"]["destination"]["station"]
        },
        "booking": {
            "platforms": booking_links,
            "recommended": booking_links[0] if booking_links else None
        },
        "recommendation": f"🚂 Taking the train saves {round(savings_kg, 0)} kg CO₂ ({round(savings_percent, 0)}% reduction)" if savings_kg > 0 else "✈️ Flight may be preferred for this route"
    })


@bp.route("/routes", methods=["GET"])
def list_routes():
    """
    List all available train routes.
    
    Query params:
        origin: Optional filter by origin
    """
    origin_filter = request.args.get("origin", "").upper()
    
    routes = []
    seen = set()
    
    for (origin, dest), data in TRAIN_ROUTES.items():
        # Avoid duplicates (we have forward and reverse)
        route_key = tuple(sorted([origin, dest]))
        if route_key in seen:
            continue
        seen.add(route_key)
        
        if origin_filter and origin != origin_filter:
            continue
        
        origin_info = TRAIN_STATIONS.get(origin, {})
        dest_info = TRAIN_STATIONS.get(dest, {})
        
        routes.append({
            "origin": origin,
            "destination": dest,
            "origin_city": origin_info.get("city", origin),
            "destination_city": dest_info.get("city", dest),
            "operator": data["operator"],
            "duration": format_duration(data["duration_minutes"]),
            "duration_minutes": data["duration_minutes"],
            "distance_km": data["distance_km"],
            "high_speed": data["high_speed"],
            "co2_kg": data["co2_per_passenger_kg"]
        })
    
    # Sort by origin city
    routes.sort(key=lambda x: (x["origin_city"], x["destination_city"]))
    
    return jsonify({
        "count": len(routes),
        "routes": routes
    })


@bp.route("/stations", methods=["GET"])
def list_stations():
    """
    List all train stations with their airport codes.
    """
    stations = []
    for code, info in TRAIN_STATIONS.items():
        stations.append({
            "airport_code": code,
            "station_name": info["name"],
            "city": info["city"],
            "country": info["country"]
        })
    
    # Sort by city
    stations.sort(key=lambda x: x["city"])
    
    return jsonify({
        "count": len(stations),
        "stations": stations
    })


@bp.route("/booking-platforms", methods=["GET"])
def list_booking_platforms():
    """
    List all supported train booking platforms.
    """
    platforms = []
    for platform_id, platform in BOOKING_PLATFORMS.items():
        platforms.append({
            "id": platform_id,
            "name": platform["name"],
            "logo": platform["logo"],
            "description": platform["description"],
            "website": platform["base_url"],
            "coverage": platform["coverage"]
        })
    
    return jsonify({
        "count": len(platforms),
        "platforms": platforms
    })


@bp.route("/book", methods=["GET"])
def get_booking_urls():
    """
    Get booking URLs for a specific route.
    
    Query params:
        origin: Origin airport code
        destination: Destination airport code
        date: Optional travel date (YYYY-MM-DD)
    """
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    date = request.args.get("date")
    
    if not origin or not destination:
        return jsonify({
            "error": "Missing required parameters",
            "required": ["origin", "destination"]
        }), 400
    
    booking_links = get_booking_links(origin, destination, date)
    
    return jsonify({
        "route": {
            "origin": origin,
            "destination": destination
        },
        "date": date,
        "platforms": booking_links
    })
