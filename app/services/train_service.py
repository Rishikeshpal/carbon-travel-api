"""
European Train Service - Provides train schedules and calculates emissions.
Data sourced from Eurostar, TGV, ICE, and other European rail operators.
"""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# =============================================================================
# BOOKING PLATFORMS
# =============================================================================

BOOKING_PLATFORMS = {
    "trainline": {
        "name": "Trainline",
        "logo": "🎫",
        "description": "Compare prices across all European operators",
        "base_url": "https://www.thetrainline.com/book/results",
        "coverage": ["all"]
    },
    "eurostar": {
        "name": "Eurostar",
        "logo": "⭐",
        "description": "Official Eurostar booking - London to Paris/Brussels/Amsterdam",
        "base_url": "https://www.eurostar.com/uk-en/train-search",
        "coverage": ["LHR", "CDG", "BRU", "AMS"]
    },
    "rail_europe": {
        "name": "Rail Europe",
        "logo": "🌍",
        "description": "Book trains across 30+ European countries",
        "base_url": "https://www.raileurope.com/en-us/train-tickets",
        "coverage": ["all"]
    },
    "sncf_connect": {
        "name": "SNCF Connect",
        "logo": "🇫🇷",
        "description": "Official French railways - TGV, Thalys, Eurostar",
        "base_url": "https://www.sncf-connect.com/en-en/train-ticket",
        "coverage": ["CDG", "LYS", "MRS", "BCN"]
    },
    "deutsche_bahn": {
        "name": "Deutsche Bahn",
        "logo": "🇩🇪",
        "description": "Official German railways - ICE high-speed trains",
        "base_url": "https://int.bahn.de/en",
        "coverage": ["FRA", "MUC", "BER", "DUS", "CGN", "HAM"]
    },
    "trenitalia": {
        "name": "Trenitalia",
        "logo": "🇮🇹",
        "description": "Official Italian railways - Frecciarossa",
        "base_url": "https://www.trenitalia.com/en.html",
        "coverage": ["FCO", "MXP", "VCE"]
    },
    "renfe": {
        "name": "Renfe",
        "logo": "🇪🇸",
        "description": "Official Spanish railways - AVE high-speed",
        "base_url": "https://www.renfe.com/es/en",
        "coverage": ["MAD", "BCN"]
    },
    "omio": {
        "name": "Omio",
        "logo": "🚂",
        "description": "Compare trains, buses, and flights across Europe",
        "base_url": "https://www.omio.com/trains",
        "coverage": ["all"]
    },
    "ns_international": {
        "name": "NS International",
        "logo": "🇳🇱",
        "description": "Dutch railways international booking",
        "base_url": "https://www.nsinternational.com/en",
        "coverage": ["AMS", "BRU"]
    }
}

# City names for booking URLs
CITY_NAMES = {
    "LHR": "London", "CDG": "Paris", "BRU": "Brussels", "AMS": "Amsterdam",
    "FRA": "Frankfurt", "MUC": "Munich", "BER": "Berlin", "DUS": "Dusseldorf",
    "CGN": "Cologne", "HAM": "Hamburg", "FCO": "Rome", "MXP": "Milan",
    "VCE": "Venice", "MAD": "Madrid", "BCN": "Barcelona", "ZRH": "Zurich",
    "GVA": "Geneva", "VIE": "Vienna", "PRG": "Prague", "LYS": "Lyon",
    "MRS": "Marseille"
}

# =============================================================================
# TRAIN STATION DATABASE (Major European Stations)
# =============================================================================

TRAIN_STATIONS = {
    # UK
    "LHR": {"station_id": "8400058", "name": "London St Pancras", "city": "London", "country": "GB"},
    "STN": {"station_id": "8400058", "name": "London St Pancras", "city": "London", "country": "GB"},
    "LGW": {"station_id": "8400058", "name": "London St Pancras", "city": "London", "country": "GB"},
    
    # France
    "CDG": {"station_id": "8727100", "name": "Paris Gare du Nord", "city": "Paris", "country": "FR"},
    "ORY": {"station_id": "8727100", "name": "Paris Gare du Nord", "city": "Paris", "country": "FR"},
    "LYS": {"station_id": "8774100", "name": "Lyon Part-Dieu", "city": "Lyon", "country": "FR"},
    "MRS": {"station_id": "8775100", "name": "Marseille St-Charles", "city": "Marseille", "country": "FR"},
    
    # Germany
    "FRA": {"station_id": "8000105", "name": "Frankfurt Hbf", "city": "Frankfurt", "country": "DE"},
    "MUC": {"station_id": "8000261", "name": "München Hbf", "city": "Munich", "country": "DE"},
    "BER": {"station_id": "8011160", "name": "Berlin Hbf", "city": "Berlin", "country": "DE"},
    "TXL": {"station_id": "8011160", "name": "Berlin Hbf", "city": "Berlin", "country": "DE"},
    "DUS": {"station_id": "8000085", "name": "Düsseldorf Hbf", "city": "Düsseldorf", "country": "DE"},
    "CGN": {"station_id": "8000207", "name": "Köln Hbf", "city": "Cologne", "country": "DE"},
    "HAM": {"station_id": "8002549", "name": "Hamburg Hbf", "city": "Hamburg", "country": "DE"},
    
    # Netherlands
    "AMS": {"station_id": "8400058", "name": "Amsterdam Centraal", "city": "Amsterdam", "country": "NL"},
    
    # Belgium
    "BRU": {"station_id": "8814001", "name": "Bruxelles-Midi", "city": "Brussels", "country": "BE"},
    
    # Switzerland
    "ZRH": {"station_id": "8503000", "name": "Zürich HB", "city": "Zurich", "country": "CH"},
    "GVA": {"station_id": "8501008", "name": "Genève Cornavin", "city": "Geneva", "country": "CH"},
    
    # Italy
    "FCO": {"station_id": "8308409", "name": "Roma Termini", "city": "Rome", "country": "IT"},
    "MXP": {"station_id": "8300046", "name": "Milano Centrale", "city": "Milan", "country": "IT"},
    "VCE": {"station_id": "8300098", "name": "Venezia Santa Lucia", "city": "Venice", "country": "IT"},
    
    # Spain
    "MAD": {"station_id": "7100010", "name": "Madrid Puerta de Atocha", "city": "Madrid", "country": "ES"},
    "BCN": {"station_id": "7171801", "name": "Barcelona Sants", "city": "Barcelona", "country": "ES"},
    
    # Austria
    "VIE": {"station_id": "8103000", "name": "Wien Hbf", "city": "Vienna", "country": "AT"},
    
    # Czech Republic
    "PRG": {"station_id": "5400014", "name": "Praha hl.n.", "city": "Prague", "country": "CZ"},
}

# Popular train routes with accurate journey data
TRAIN_ROUTES = {
    # Eurostar routes
    ("LHR", "CDG"): {
        "operator": "Eurostar",
        "duration_minutes": 137,
        "distance_km": 460,
        "stops": ["London St Pancras", "Ebbsfleet Intl", "Lille Europe", "Paris Gare du Nord"],
        "frequency": "18 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 6.0
    },
    ("LHR", "BRU"): {
        "operator": "Eurostar",
        "duration_minutes": 120,
        "distance_km": 370,
        "stops": ["London St Pancras", "Ebbsfleet Intl", "Bruxelles-Midi"],
        "frequency": "10 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 4.8
    },
    ("LHR", "AMS"): {
        "operator": "Eurostar",
        "duration_minutes": 228,
        "distance_km": 450,
        "stops": ["London St Pancras", "Ebbsfleet Intl", "Bruxelles-Midi", "Rotterdam Centraal", "Amsterdam Centraal"],
        "frequency": "5 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 5.9
    },
    
    # TGV routes (France)
    ("CDG", "LYS"): {
        "operator": "TGV",
        "duration_minutes": 120,
        "distance_km": 470,
        "stops": ["Paris Gare de Lyon", "Lyon Part-Dieu"],
        "frequency": "25 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 2.4
    },
    ("CDG", "MRS"): {
        "operator": "TGV",
        "duration_minutes": 195,
        "distance_km": 775,
        "stops": ["Paris Gare de Lyon", "Avignon TGV", "Marseille St-Charles"],
        "frequency": "15 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 4.0
    },
    ("CDG", "BCN"): {
        "operator": "TGV",
        "duration_minutes": 390,
        "distance_km": 1050,
        "stops": ["Paris Gare de Lyon", "Montpellier", "Perpignan", "Figueres", "Girona", "Barcelona Sants"],
        "frequency": "4 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 5.5
    },
    
    # ICE routes (Germany)
    ("FRA", "MUC"): {
        "operator": "ICE",
        "duration_minutes": 195,
        "distance_km": 400,
        "stops": ["Frankfurt Hbf", "Mannheim Hbf", "Stuttgart Hbf", "Ulm Hbf", "München Hbf"],
        "frequency": "30 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 8.0
    },
    ("FRA", "BER"): {
        "operator": "ICE",
        "duration_minutes": 240,
        "distance_km": 550,
        "stops": ["Frankfurt Hbf", "Fulda", "Erfurt Hbf", "Halle Hbf", "Berlin Hbf"],
        "frequency": "25 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 11.0
    },
    ("FRA", "CGN"): {
        "operator": "ICE",
        "duration_minutes": 62,
        "distance_km": 190,
        "stops": ["Frankfurt Hbf", "Frankfurt Flughafen", "Köln Hbf"],
        "frequency": "35 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 3.8
    },
    ("MUC", "VIE"): {
        "operator": "ICE/ÖBB",
        "duration_minutes": 240,
        "distance_km": 430,
        "stops": ["München Hbf", "Rosenheim", "Salzburg Hbf", "Linz Hbf", "Wien Hbf"],
        "frequency": "12 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 8.6
    },
    
    # Thalys routes
    ("CDG", "BRU"): {
        "operator": "Thalys",
        "duration_minutes": 82,
        "distance_km": 310,
        "stops": ["Paris Gare du Nord", "Bruxelles-Midi"],
        "frequency": "20 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 3.2
    },
    ("CDG", "AMS"): {
        "operator": "Thalys",
        "duration_minutes": 195,
        "distance_km": 500,
        "stops": ["Paris Gare du Nord", "Bruxelles-Midi", "Antwerpen Centraal", "Rotterdam Centraal", "Schiphol", "Amsterdam Centraal"],
        "frequency": "10 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 5.2
    },
    ("CDG", "CGN"): {
        "operator": "Thalys",
        "duration_minutes": 195,
        "distance_km": 490,
        "stops": ["Paris Gare du Nord", "Bruxelles-Midi", "Liège-Guillemins", "Aachen Hbf", "Köln Hbf"],
        "frequency": "6 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 5.1
    },
    
    # Italy routes
    ("FCO", "MXP"): {
        "operator": "Frecciarossa",
        "duration_minutes": 175,
        "distance_km": 600,
        "stops": ["Roma Termini", "Firenze SMN", "Bologna Centrale", "Milano Centrale"],
        "frequency": "30 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 12.0
    },
    ("MXP", "VCE"): {
        "operator": "Frecciarossa",
        "duration_minutes": 145,
        "distance_km": 270,
        "stops": ["Milano Centrale", "Verona Porta Nuova", "Venezia Mestre", "Venezia Santa Lucia"],
        "frequency": "20 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 5.4
    },
    
    # Spain routes
    ("MAD", "BCN"): {
        "operator": "AVE",
        "duration_minutes": 155,
        "distance_km": 620,
        "stops": ["Madrid Puerta de Atocha", "Zaragoza Delicias", "Lleida Pirineus", "Barcelona Sants"],
        "frequency": "25 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 12.4
    },
    
    # Cross-border routes
    ("ZRH", "MXP"): {
        "operator": "SBB/Trenitalia",
        "duration_minutes": 205,
        "distance_km": 280,
        "stops": ["Zürich HB", "Arth-Goldau", "Lugano", "Como", "Milano Centrale"],
        "frequency": "8 trains/day",
        "high_speed": False,
        "co2_per_passenger_kg": 5.6
    },
    ("VIE", "PRG"): {
        "operator": "ÖBB/ČD",
        "duration_minutes": 240,
        "distance_km": 330,
        "stops": ["Wien Hbf", "Břeclav", "Brno hl.n.", "Praha hl.n."],
        "frequency": "8 trains/day",
        "high_speed": False,
        "co2_per_passenger_kg": 6.6
    },
    ("BRU", "AMS"): {
        "operator": "Thalys/NS",
        "duration_minutes": 113,
        "distance_km": 210,
        "stops": ["Bruxelles-Midi", "Antwerpen Centraal", "Rotterdam Centraal", "Schiphol", "Amsterdam Centraal"],
        "frequency": "15 trains/day",
        "high_speed": True,
        "co2_per_passenger_kg": 2.2
    },
}

# Add reverse routes
_reverse_routes = {}
for (origin, dest), data in TRAIN_ROUTES.items():
    _reverse_routes[(dest, origin)] = {
        **data,
        "stops": list(reversed(data["stops"]))
    }
TRAIN_ROUTES.update(_reverse_routes)


@dataclass
class TrainJourney:
    """Represents a train journey."""
    origin: str
    destination: str
    origin_station: str
    destination_station: str
    operator: str
    duration_minutes: int
    distance_km: int
    stops: list
    stop_count: int
    frequency: str
    high_speed: bool
    co2_kg: float
    departure_times: list
    price_estimate_eur: Optional[float] = None


def get_train_route(origin: str, destination: str) -> Optional[TrainJourney]:
    """
    Get train route between two airports/cities.
    
    Args:
        origin: Origin airport code (e.g., "LHR")
        destination: Destination airport code (e.g., "CDG")
    
    Returns:
        TrainJourney object if route exists, None otherwise
    """
    origin = origin.upper()
    destination = destination.upper()
    
    route_key = (origin, destination)
    route_data = TRAIN_ROUTES.get(route_key)
    
    if not route_data:
        return None
    
    origin_station = TRAIN_STATIONS.get(origin, {})
    dest_station = TRAIN_STATIONS.get(destination, {})
    
    # Generate sample departure times
    base_times = ["06:00", "07:30", "09:00", "10:30", "12:00", "14:00", "16:00", "18:00", "20:00"]
    
    return TrainJourney(
        origin=origin,
        destination=destination,
        origin_station=origin_station.get("name", route_data["stops"][0]),
        destination_station=dest_station.get("name", route_data["stops"][-1]),
        operator=route_data["operator"],
        duration_minutes=route_data["duration_minutes"],
        distance_km=route_data["distance_km"],
        stops=route_data["stops"],
        stop_count=len(route_data["stops"]),
        frequency=route_data["frequency"],
        high_speed=route_data["high_speed"],
        co2_kg=route_data["co2_per_passenger_kg"],
        departure_times=base_times[:6]
    )


def format_duration(minutes: int) -> str:
    """Format duration in hours and minutes."""
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def search_train_journeys(origin: str, destination: str, date: str = None) -> dict:
    """
    Search for train journeys between two points.
    Returns detailed journey information.
    """
    journey = get_train_route(origin, destination)
    
    if not journey:
        return {
            "found": False,
            "message": f"No direct high-speed train route found between {origin} and {destination}",
            "suggestion": "Consider connecting flights or multi-leg train journeys"
        }
    
    return {
        "found": True,
        "route": {
            "origin": {
                "airport": origin,
                "station": journey.origin_station,
                "city": TRAIN_STATIONS.get(origin, {}).get("city", origin)
            },
            "destination": {
                "airport": destination,
                "station": journey.destination_station,
                "city": TRAIN_STATIONS.get(destination, {}).get("city", destination)
            }
        },
        "journey": {
            "operator": journey.operator,
            "duration": format_duration(journey.duration_minutes),
            "duration_minutes": journey.duration_minutes,
            "distance_km": journey.distance_km,
            "high_speed": journey.high_speed
        },
        "stations": {
            "count": journey.stop_count,
            "list": journey.stops
        },
        "schedule": {
            "frequency": journey.frequency,
            "sample_departures": journey.departure_times
        },
        "emissions": {
            "co2_kg": journey.co2_kg,
            "per_km": round(journey.co2_kg / journey.distance_km * 1000, 2),
            "source": "UIC Railway Handbook / Operator data"
        }
    }


def get_booking_links(origin: str, destination: str, date: str = None) -> list:
    """
    Generate booking links for various train platforms.
    
    Args:
        origin: Origin airport code
        destination: Destination airport code
        date: Optional travel date (YYYY-MM-DD)
    
    Returns:
        List of booking platform info with URLs
    """
    from urllib.parse import quote
    
    origin = origin.upper()
    destination = destination.upper()
    
    # Get station info
    origin_station_info = TRAIN_STATIONS.get(origin, {})
    dest_station_info = TRAIN_STATIONS.get(destination, {})
    
    origin_city = CITY_NAMES.get(origin, origin)
    dest_city = CITY_NAMES.get(destination, destination)
    
    origin_station = origin_station_info.get("name", origin_city)
    dest_station = dest_station_info.get("name", dest_city)
    
    # URL encode
    origin_city_encoded = quote(origin_city)
    dest_city_encoded = quote(dest_city)
    origin_station_encoded = quote(origin_station)
    dest_station_encoded = quote(dest_station)
    
    # Default date is 7 days from now
    if not date:
        date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Format date for different platforms
    date_parts = date.split("-")
    date_dmy = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}" if len(date_parts) == 3 else date
    
    booking_links = []
    
    for platform_id, platform in BOOKING_PLATFORMS.items():
        # Check if platform covers this route
        covers_route = (
            "all" in platform["coverage"] or
            origin in platform["coverage"] or
            destination in platform["coverage"]
        )
        
        if not covers_route:
            continue
        
        # Generate platform-specific URLs that actually work
        if platform_id == "trainline":
            # Trainline deep link with date (confirmed working format)
            url = f"https://www.thetrainline.com/book/results?origin={origin_city}&destination={dest_city}&outwardDate={date}&journeySearchType=single"
        
        elif platform_id == "eurostar":
            # Eurostar main booking page
            url = "https://www.eurostar.com/uk-en/book-eurostar"
        
        elif platform_id == "rail_europe":
            # Rail Europe main page
            url = "https://www.raileurope.com/en-us"
        
        elif platform_id == "sncf_connect":
            # SNCF Connect main booking
            url = "https://www.sncf-connect.com/en-en/"
        
        elif platform_id == "deutsche_bahn":
            # DB International booking
            url = "https://int.bahn.de/en"
        
        elif platform_id == "trenitalia":
            url = "https://www.trenitalia.com/en.html"
        
        elif platform_id == "renfe":
            url = "https://www.renfe.com/es/en"
        
        elif platform_id == "omio":
            # Omio search with date
            url = f"https://www.omio.com/search?from={origin_city}&to={dest_city}&date={date}&transportModes=train"
        
        elif platform_id == "ns_international":
            url = "https://www.nsinternational.com/en"
        
        else:
            url = platform["base_url"]
        
        booking_links.append({
            "platform": platform["name"],
            "logo": platform["logo"],
            "description": platform["description"],
            "url": url,
            "origin_station": origin_station,
            "destination_station": dest_station,
            "origin_city": origin_city,
            "destination_city": dest_city,
            "travel_date": date
        })
    
    # Sort: prioritize platforms that work well
    priority_order = ["trainline", "omio", "rail_europe", "eurostar", "deutsche_bahn", "sncf_connect", "trenitalia", "renfe", "ns_international"]
    
    def sort_key(x):
        platform_lower = x["platform"].lower().replace(" ", "_")
        for p_id, p_info in BOOKING_PLATFORMS.items():
            if p_info["name"] == x["platform"]:
                try:
                    return priority_order.index(p_id)
                except ValueError:
                    return 99
        return 99
    
    booking_links.sort(key=sort_key)
    
    return booking_links


def compare_train_vs_flight(origin: str, destination: str, flight_emissions_kg: float) -> dict:
    """
    Compare train and flight emissions for a route.
    """
    train_data = search_train_journeys(origin, destination)
    
    if not train_data["found"]:
        return {
            "train_available": False,
            "message": train_data["message"]
        }
    
    train_emissions = train_data["emissions"]["co2_kg"]
    savings_kg = flight_emissions_kg - train_emissions
    savings_percent = (savings_kg / flight_emissions_kg) * 100 if flight_emissions_kg > 0 else 0
    
    return {
        "train_available": True,
        "comparison": {
            "flight_co2_kg": round(flight_emissions_kg, 1),
            "train_co2_kg": round(train_emissions, 1),
            "savings_kg": round(savings_kg, 1),
            "savings_percent": round(savings_percent, 1),
            "train_is_greener": savings_kg > 0
        },
        "train_details": train_data,
        "recommendation": f"Taking the train saves {round(savings_kg, 0)} kg CO₂ ({round(savings_percent, 0)}% less emissions)"
    }
