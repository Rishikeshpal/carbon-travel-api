"""
Regional electricity grid carbon intensity data.
Based on ENTSO-E (Europe), EPA eGRID (US), and IEA data.

All values in gCO₂/kWh (grams of CO₂ per kilowatt-hour).
"""

from typing import Optional

# Grid carbon intensity by country (gCO₂/kWh)
# Sources: ENTSO-E 2024, EPA eGRID 2024, IEA 2024
GRID_INTENSITY: dict[str, dict] = {
    # EU - Very Low Carbon (Nuclear/Hydro dominant)
    "FR": {"intensity": 56, "source": "ENTSO-E 2024", "quality": "measured", "notes": "~70% nuclear"},
    "SE": {"intensity": 41, "source": "ENTSO-E 2024", "quality": "measured", "notes": "Hydro + nuclear"},
    "NO": {"intensity": 29, "source": "ENTSO-E 2024", "quality": "measured", "notes": "~95% hydro"},
    "FI": {"intensity": 131, "source": "ENTSO-E 2024", "quality": "measured", "notes": "Nuclear + hydro"},
    "CH": {"intensity": 48, "source": "IEA 2024", "quality": "measured", "notes": "Hydro + nuclear"},
    "AT": {"intensity": 108, "source": "ENTSO-E 2024", "quality": "measured", "notes": "Hydro dominant"},
    
    # EU - Low Carbon
    "BE": {"intensity": 167, "source": "ENTSO-E 2024", "quality": "measured"},
    "DK": {"intensity": 158, "source": "ENTSO-E 2024", "quality": "measured", "notes": "High wind"},
    "ES": {"intensity": 161, "source": "ENTSO-E 2024", "quality": "measured"},
    "PT": {"intensity": 178, "source": "ENTSO-E 2024", "quality": "measured"},
    "LU": {"intensity": 89, "source": "ENTSO-E 2024", "quality": "measured"},
    
    # EU - Medium Carbon
    "IT": {"intensity": 267, "source": "ENTSO-E 2024", "quality": "measured"},
    "GB": {"intensity": 198, "source": "National Grid 2024", "quality": "measured"},
    "IE": {"intensity": 296, "source": "ENTSO-E 2024", "quality": "measured"},
    "NL": {"intensity": 328, "source": "ENTSO-E 2024", "quality": "measured"},
    "HU": {"intensity": 223, "source": "ENTSO-E 2024", "quality": "measured"},
    "SK": {"intensity": 168, "source": "ENTSO-E 2024", "quality": "measured"},
    "SI": {"intensity": 232, "source": "ENTSO-E 2024", "quality": "measured"},
    "HR": {"intensity": 187, "source": "ENTSO-E 2024", "quality": "measured"},
    
    # EU - High Carbon (Coal dependent)
    "DE": {"intensity": 366, "source": "ENTSO-E 2024", "quality": "measured", "notes": "Coal phase-out ongoing"},
    "PL": {"intensity": 773, "source": "ENTSO-E 2024", "quality": "measured", "notes": "~70% coal"},
    "CZ": {"intensity": 436, "source": "ENTSO-E 2024", "quality": "measured"},
    "GR": {"intensity": 341, "source": "ENTSO-E 2024", "quality": "measured"},
    "RO": {"intensity": 298, "source": "ENTSO-E 2024", "quality": "measured"},
    "BG": {"intensity": 412, "source": "ENTSO-E 2024", "quality": "measured"},
    "EE": {"intensity": 723, "source": "ENTSO-E 2024", "quality": "measured", "notes": "Oil shale"},
    
    # Non-EU Europe
    "TR": {"intensity": 438, "source": "IEA 2024", "quality": "estimated"},
    "RS": {"intensity": 719, "source": "IEA 2024", "quality": "estimated"},
    "UA": {"intensity": 285, "source": "IEA 2024", "quality": "estimated"},
    "IS": {"intensity": 28, "source": "IEA 2024", "quality": "measured", "notes": "Geothermal + hydro"},
    
    # North America
    "US": {"intensity": 386, "source": "EPA eGRID 2024", "quality": "measured", "notes": "National average"},
    "CA": {"intensity": 120, "source": "IEA 2024", "quality": "measured", "notes": "Hydro dominant"},
    "MX": {"intensity": 435, "source": "IEA 2024", "quality": "estimated"},
    
    # Middle East
    "AE": {"intensity": 415, "source": "IEA 2024", "quality": "estimated", "notes": "Gas dominant"},
    "SA": {"intensity": 530, "source": "IEA 2024", "quality": "estimated"},
    "QA": {"intensity": 397, "source": "IEA 2024", "quality": "estimated"},
    "IL": {"intensity": 465, "source": "IEA 2024", "quality": "estimated"},
    "KW": {"intensity": 573, "source": "IEA 2024", "quality": "estimated"},
    
    # Asia Pacific
    "JP": {"intensity": 459, "source": "IEA 2024", "quality": "measured"},
    "KR": {"intensity": 436, "source": "IEA 2024", "quality": "measured"},
    "CN": {"intensity": 555, "source": "IEA 2024", "quality": "estimated"},
    "IN": {"intensity": 708, "source": "IEA 2024", "quality": "estimated"},
    "SG": {"intensity": 408, "source": "IEA 2024", "quality": "measured"},
    "HK": {"intensity": 619, "source": "IEA 2024", "quality": "estimated"},
    "TH": {"intensity": 449, "source": "IEA 2024", "quality": "estimated"},
    "MY": {"intensity": 543, "source": "IEA 2024", "quality": "estimated"},
    "ID": {"intensity": 667, "source": "IEA 2024", "quality": "estimated"},
    "VN": {"intensity": 485, "source": "IEA 2024", "quality": "estimated"},
    "PH": {"intensity": 547, "source": "IEA 2024", "quality": "estimated"},
    "AU": {"intensity": 505, "source": "IEA 2024", "quality": "measured"},
    "NZ": {"intensity": 118, "source": "IEA 2024", "quality": "measured", "notes": "High renewable"},
    
    # South America
    "BR": {"intensity": 103, "source": "IEA 2024", "quality": "measured", "notes": "High hydro"},
    "AR": {"intensity": 338, "source": "IEA 2024", "quality": "estimated"},
    "CL": {"intensity": 351, "source": "IEA 2024", "quality": "estimated"},
    "CO": {"intensity": 175, "source": "IEA 2024", "quality": "estimated"},
    "PE": {"intensity": 283, "source": "IEA 2024", "quality": "estimated"},
    
    # Africa
    "ZA": {"intensity": 709, "source": "IEA 2024", "quality": "measured", "notes": "Coal dominant"},
    "EG": {"intensity": 442, "source": "IEA 2024", "quality": "estimated"},
    "MA": {"intensity": 610, "source": "IEA 2024", "quality": "estimated"},
    "NG": {"intensity": 391, "source": "IEA 2024", "quality": "estimated"},
    "KE": {"intensity": 127, "source": "IEA 2024", "quality": "estimated", "notes": "Geothermal"},
    "GH": {"intensity": 314, "source": "IEA 2024", "quality": "estimated"},
    "TZ": {"intensity": 347, "source": "IEA 2024", "quality": "estimated"},
}

# Global default for unknown countries (IPCC world average)
DEFAULT_INTENSITY = {
    "intensity": 475,
    "source": "IPCC 2024 global average",
    "quality": "default"
}


def get_grid_intensity(country_code: str) -> dict:
    """
    Get grid carbon intensity for a country.
    Returns the country-specific data or global default.
    """
    country = country_code.upper()
    if country in GRID_INTENSITY:
        return {
            "country_code": country,
            **GRID_INTENSITY[country]
        }
    return {
        "country_code": country,
        **DEFAULT_INTENSITY
    }


def get_intensity_value(country_code: str) -> float:
    """Get just the intensity value in gCO₂/kWh."""
    return get_grid_intensity(country_code)["intensity"]


def get_all_eu_intensities() -> dict[str, dict]:
    """Get grid intensities for all EU countries."""
    eu_countries = ["AT", "BE", "BG", "HR", "CZ", "DK", "EE", "FI", "FR", "DE", 
                    "GR", "HU", "IE", "IT", "LU", "NL", "PL", "PT", "RO", "SK", 
                    "SI", "ES", "SE"]
    return {code: GRID_INTENSITY.get(code, DEFAULT_INTENSITY) for code in eu_countries}
