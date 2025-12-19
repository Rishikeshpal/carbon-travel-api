"""
Airport database with coordinates for distance calculation.
Based on real IATA airport data.
"""

from math import radians, sin, cos, sqrt, atan2
from typing import Optional, Tuple

# Major airports with coordinates (lat, lon) and city/country info
# This is a subset - in production, use a full IATA database
AIRPORTS: dict[str, dict] = {
    # United Kingdom
    "LHR": {"name": "London Heathrow", "city": "London", "country": "GB", "lat": 51.4700, "lon": -0.4543},
    "LGW": {"name": "London Gatwick", "city": "London", "country": "GB", "lat": 51.1537, "lon": -0.1821},
    "STN": {"name": "London Stansted", "city": "London", "country": "GB", "lat": 51.8850, "lon": 0.2350},
    "LTN": {"name": "London Luton", "city": "London", "country": "GB", "lat": 51.8747, "lon": -0.3683},
    "MAN": {"name": "Manchester", "city": "Manchester", "country": "GB", "lat": 53.3537, "lon": -2.2750},
    "EDI": {"name": "Edinburgh", "city": "Edinburgh", "country": "GB", "lat": 55.9500, "lon": -3.3725},
    "BHX": {"name": "Birmingham", "city": "Birmingham", "country": "GB", "lat": 52.4539, "lon": -1.7480},
    
    # France
    "CDG": {"name": "Paris Charles de Gaulle", "city": "Paris", "country": "FR", "lat": 49.0097, "lon": 2.5479},
    "ORY": {"name": "Paris Orly", "city": "Paris", "country": "FR", "lat": 48.7233, "lon": 2.3794},
    "NCE": {"name": "Nice Côte d'Azur", "city": "Nice", "country": "FR", "lat": 43.6584, "lon": 7.2159},
    "LYS": {"name": "Lyon Saint-Exupéry", "city": "Lyon", "country": "FR", "lat": 45.7256, "lon": 5.0811},
    "MRS": {"name": "Marseille Provence", "city": "Marseille", "country": "FR", "lat": 43.4393, "lon": 5.2214},
    
    # Germany
    "FRA": {"name": "Frankfurt", "city": "Frankfurt", "country": "DE", "lat": 50.0379, "lon": 8.5622},
    "MUC": {"name": "Munich", "city": "Munich", "country": "DE", "lat": 48.3538, "lon": 11.7861},
    "TXL": {"name": "Berlin Tegel", "city": "Berlin", "country": "DE", "lat": 52.5597, "lon": 13.2877},
    "BER": {"name": "Berlin Brandenburg", "city": "Berlin", "country": "DE", "lat": 52.3667, "lon": 13.5033},
    "DUS": {"name": "Düsseldorf", "city": "Düsseldorf", "country": "DE", "lat": 51.2895, "lon": 6.7668},
    "HAM": {"name": "Hamburg", "city": "Hamburg", "country": "DE", "lat": 53.6304, "lon": 9.9882},
    
    # Netherlands
    "AMS": {"name": "Amsterdam Schiphol", "city": "Amsterdam", "country": "NL", "lat": 52.3105, "lon": 4.7683},
    
    # Belgium
    "BRU": {"name": "Brussels", "city": "Brussels", "country": "BE", "lat": 50.9014, "lon": 4.4844},
    
    # Spain
    "MAD": {"name": "Madrid Barajas", "city": "Madrid", "country": "ES", "lat": 40.4983, "lon": -3.5676},
    "BCN": {"name": "Barcelona El Prat", "city": "Barcelona", "country": "ES", "lat": 41.2971, "lon": 2.0785},
    
    # Italy
    "FCO": {"name": "Rome Fiumicino", "city": "Rome", "country": "IT", "lat": 41.8003, "lon": 12.2389},
    "MXP": {"name": "Milan Malpensa", "city": "Milan", "country": "IT", "lat": 45.6306, "lon": 8.7281},
    "LIN": {"name": "Milan Linate", "city": "Milan", "country": "IT", "lat": 45.4497, "lon": 9.2783},
    "VCE": {"name": "Venice Marco Polo", "city": "Venice", "country": "IT", "lat": 45.5053, "lon": 12.3519},
    
    # Switzerland
    "ZRH": {"name": "Zurich", "city": "Zurich", "country": "CH", "lat": 47.4647, "lon": 8.5492},
    "GVA": {"name": "Geneva", "city": "Geneva", "country": "CH", "lat": 46.2381, "lon": 6.1089},
    
    # Austria
    "VIE": {"name": "Vienna", "city": "Vienna", "country": "AT", "lat": 48.1103, "lon": 16.5697},
    
    # Portugal
    "LIS": {"name": "Lisbon", "city": "Lisbon", "country": "PT", "lat": 38.7756, "lon": -9.1354},
    
    # Ireland
    "DUB": {"name": "Dublin", "city": "Dublin", "country": "IE", "lat": 53.4213, "lon": -6.2701},
    
    # Scandinavia
    "CPH": {"name": "Copenhagen", "city": "Copenhagen", "country": "DK", "lat": 55.6180, "lon": 12.6508},
    "ARN": {"name": "Stockholm Arlanda", "city": "Stockholm", "country": "SE", "lat": 59.6519, "lon": 17.9186},
    "OSL": {"name": "Oslo Gardermoen", "city": "Oslo", "country": "NO", "lat": 60.1939, "lon": 11.1004},
    "HEL": {"name": "Helsinki", "city": "Helsinki", "country": "FI", "lat": 60.3172, "lon": 24.9633},
    
    # Poland
    "WAW": {"name": "Warsaw Chopin", "city": "Warsaw", "country": "PL", "lat": 52.1657, "lon": 20.9671},
    
    # Czech Republic
    "PRG": {"name": "Prague", "city": "Prague", "country": "CZ", "lat": 50.1008, "lon": 14.2600},
    
    # Greece
    "ATH": {"name": "Athens", "city": "Athens", "country": "GR", "lat": 37.9364, "lon": 23.9445},
    
    # Turkey
    "IST": {"name": "Istanbul", "city": "Istanbul", "country": "TR", "lat": 41.2753, "lon": 28.7519},
    
    # United States
    "JFK": {"name": "New York JFK", "city": "New York", "country": "US", "lat": 40.6413, "lon": -73.7781},
    "EWR": {"name": "Newark", "city": "New York", "country": "US", "lat": 40.6895, "lon": -74.1745},
    "LAX": {"name": "Los Angeles", "city": "Los Angeles", "country": "US", "lat": 33.9416, "lon": -118.4085},
    "SFO": {"name": "San Francisco", "city": "San Francisco", "country": "US", "lat": 37.6213, "lon": -122.3790},
    "ORD": {"name": "Chicago O'Hare", "city": "Chicago", "country": "US", "lat": 41.9742, "lon": -87.9073},
    "MIA": {"name": "Miami", "city": "Miami", "country": "US", "lat": 25.7959, "lon": -80.2870},
    "BOS": {"name": "Boston Logan", "city": "Boston", "country": "US", "lat": 42.3656, "lon": -71.0096},
    "DFW": {"name": "Dallas/Fort Worth", "city": "Dallas", "country": "US", "lat": 32.8998, "lon": -97.0403},
    "ATL": {"name": "Atlanta", "city": "Atlanta", "country": "US", "lat": 33.6407, "lon": -84.4277},
    "SEA": {"name": "Seattle-Tacoma", "city": "Seattle", "country": "US", "lat": 47.4502, "lon": -122.3088},
    
    # Canada
    "YYZ": {"name": "Toronto Pearson", "city": "Toronto", "country": "CA", "lat": 43.6777, "lon": -79.6248},
    "YVR": {"name": "Vancouver", "city": "Vancouver", "country": "CA", "lat": 49.1947, "lon": -123.1792},
    "YUL": {"name": "Montreal Trudeau", "city": "Montreal", "country": "CA", "lat": 45.4706, "lon": -73.7408},
    
    # Middle East
    "DXB": {"name": "Dubai", "city": "Dubai", "country": "AE", "lat": 25.2532, "lon": 55.3657},
    "DOH": {"name": "Doha Hamad", "city": "Doha", "country": "QA", "lat": 25.2731, "lon": 51.6081},
    "AUH": {"name": "Abu Dhabi", "city": "Abu Dhabi", "country": "AE", "lat": 24.4330, "lon": 54.6511},
    "TLV": {"name": "Tel Aviv Ben Gurion", "city": "Tel Aviv", "country": "IL", "lat": 32.0055, "lon": 34.8854},
    
    # Asia
    "SIN": {"name": "Singapore Changi", "city": "Singapore", "country": "SG", "lat": 1.3644, "lon": 103.9915},
    "HKG": {"name": "Hong Kong", "city": "Hong Kong", "country": "HK", "lat": 22.3080, "lon": 113.9185},
    "NRT": {"name": "Tokyo Narita", "city": "Tokyo", "country": "JP", "lat": 35.7720, "lon": 140.3929},
    "HND": {"name": "Tokyo Haneda", "city": "Tokyo", "country": "JP", "lat": 35.5494, "lon": 139.7798},
    "ICN": {"name": "Seoul Incheon", "city": "Seoul", "country": "KR", "lat": 37.4602, "lon": 126.4407},
    "PEK": {"name": "Beijing Capital", "city": "Beijing", "country": "CN", "lat": 40.0799, "lon": 116.6031},
    "PVG": {"name": "Shanghai Pudong", "city": "Shanghai", "country": "CN", "lat": 31.1443, "lon": 121.8083},
    "BKK": {"name": "Bangkok Suvarnabhumi", "city": "Bangkok", "country": "TH", "lat": 13.6900, "lon": 100.7501},
    "DEL": {"name": "Delhi Indira Gandhi", "city": "Delhi", "country": "IN", "lat": 28.5562, "lon": 77.1000},
    "BOM": {"name": "Mumbai", "city": "Mumbai", "country": "IN", "lat": 19.0896, "lon": 72.8656},
    
    # Australia/Oceania
    "SYD": {"name": "Sydney", "city": "Sydney", "country": "AU", "lat": -33.9399, "lon": 151.1753},
    "MEL": {"name": "Melbourne", "city": "Melbourne", "country": "AU", "lat": -37.6690, "lon": 144.8410},
    "AKL": {"name": "Auckland", "city": "Auckland", "country": "NZ", "lat": -37.0082, "lon": 174.7850},
    
    # South America
    "GRU": {"name": "São Paulo Guarulhos", "city": "São Paulo", "country": "BR", "lat": -23.4356, "lon": -46.4731},
    "EZE": {"name": "Buenos Aires Ezeiza", "city": "Buenos Aires", "country": "AR", "lat": -34.8222, "lon": -58.5358},
    "SCL": {"name": "Santiago", "city": "Santiago", "country": "CL", "lat": -33.3930, "lon": -70.7858},
    "BOG": {"name": "Bogotá El Dorado", "city": "Bogotá", "country": "CO", "lat": 4.7016, "lon": -74.1469},
    
    # Africa
    "JNB": {"name": "Johannesburg", "city": "Johannesburg", "country": "ZA", "lat": -26.1367, "lon": 28.2411},
    "CPT": {"name": "Cape Town", "city": "Cape Town", "country": "ZA", "lat": -33.9715, "lon": 18.6021},
    "CAI": {"name": "Cairo", "city": "Cairo", "country": "EG", "lat": 30.1219, "lon": 31.4056},
    "NBO": {"name": "Nairobi Jomo Kenyatta", "city": "Nairobi", "country": "KE", "lat": -1.3192, "lon": 36.9278},
    "CMN": {"name": "Casablanca Mohammed V", "city": "Casablanca", "country": "MA", "lat": 33.3675, "lon": -7.5900},
}


def get_airport(code: str) -> Optional[dict]:
    """Get airport information by IATA code."""
    return AIRPORTS.get(code.upper())


def get_coordinates(code: str) -> Optional[Tuple[float, float]]:
    """Get airport coordinates (lat, lon) by IATA code."""
    airport = get_airport(code)
    if airport:
        return (airport["lat"], airport["lon"])
    return None


def calculate_distance_km(origin: str, destination: str) -> Optional[float]:
    """
    Calculate great-circle distance between two airports using Haversine formula.
    Returns distance in kilometers.
    """
    origin_coords = get_coordinates(origin)
    dest_coords = get_coordinates(destination)
    
    if not origin_coords or not dest_coords:
        return None
    
    lat1, lon1 = origin_coords
    lat2, lon2 = dest_coords
    
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    # Haversine formula
    a = sin(delta_lat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    
    return round(distance, 1)


def get_haul_type(distance_km: float) -> str:
    """
    Classify flight by haul type based on distance.
    
    - Short haul: < 1,500 km
    - Medium haul: 1,500 - 4,000 km
    - Long haul: > 4,000 km
    """
    if distance_km < 1500:
        return "short"
    elif distance_km <= 4000:
        return "medium"
    else:
        return "long"
