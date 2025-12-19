"""
Confidence scoring for emission calculations.
"""

from typing import Optional


def calculate_confidence_score(
    factors: list[dict],
    has_carrier_data: bool = False,
    has_aircraft_data: bool = False,
    has_hotel_chain_data: bool = False,
    grid_data_quality: str = "default",
    haul_type: Optional[str] = None
) -> dict:
    """
    Calculate overall confidence score for an assessment.
    
    The score represents how confident we are in the accuracy of the
    emission calculations, based on the quality and specificity of
    available data.
    
    Args:
        factors: List of confidence factors from individual calculations
        has_carrier_data: Whether airline-specific data was used
        has_aircraft_data: Whether specific aircraft type was known
        has_hotel_chain_data: Whether hotel chain sustainability data was used
        grid_data_quality: Quality of grid carbon intensity data
        haul_type: Flight haul type (short/medium/long)
    
    Returns:
        Dictionary with score, level, and contributing factors
    """
    # Start with base score
    base_score = 0.65
    
    all_factors = list(factors)  # Copy input factors
    
    # Add points for positive factors, subtract for negative
    score_adjustments = 0.0
    
    # Carrier-specific data
    if has_carrier_data:
        score_adjustments += 0.05
        all_factors.append({
            "factor": "airline_specific_data",
            "impact": "positive",
            "description": "Carrier-specific fuel efficiency data used"
        })
    
    # Aircraft type known
    if has_aircraft_data:
        score_adjustments += 0.05
        all_factors.append({
            "factor": "aircraft_type_known",
            "impact": "positive",
            "description": "Specific aircraft type improves accuracy"
        })
    
    # Grid data quality
    if grid_data_quality == "measured":
        score_adjustments += 0.10
        all_factors.append({
            "factor": "measured_grid_intensity",
            "impact": "positive",
            "description": "Country has measured grid carbon intensity data"
        })
    elif grid_data_quality == "estimated":
        score_adjustments += 0.03
        all_factors.append({
            "factor": "estimated_grid_intensity",
            "impact": "neutral",
            "description": "Grid intensity based on regional estimates"
        })
    else:  # default
        score_adjustments -= 0.10
        all_factors.append({
            "factor": "default_grid_intensity",
            "impact": "negative",
            "description": "Using global default for grid intensity"
        })
    
    # Haul type confidence
    if haul_type == "short":
        score_adjustments += 0.05
        all_factors.append({
            "factor": "short_haul_accuracy",
            "impact": "positive",
            "description": "Short-haul routes have highest data accuracy"
        })
    elif haul_type == "long":
        score_adjustments += 0.02
        all_factors.append({
            "factor": "long_haul_route",
            "impact": "neutral",
            "description": "Long-haul routes use averaged factors"
        })
    
    # Hotel chain data
    if has_hotel_chain_data:
        score_adjustments += 0.08
        all_factors.append({
            "factor": "hotel_chain_data",
            "impact": "positive",
            "description": "Hotel chain-specific sustainability data available"
        })
    
    # Calculate final score
    final_score = min(1.0, max(0.0, base_score + score_adjustments))
    
    # Determine level
    if final_score >= 0.80:
        level = "high"
    elif final_score >= 0.60:
        level = "medium"
    else:
        level = "low"
    
    # Deduplicate factors
    seen = set()
    unique_factors = []
    for f in all_factors:
        key = f.get("factor", "")
        if key not in seen:
            seen.add(key)
            unique_factors.append(f)
    
    return {
        "score": round(final_score, 2),
        "level": level,
        "factors": unique_factors
    }


def aggregate_confidence_factors(results: list) -> list[dict]:
    """
    Aggregate confidence factors from multiple calculation results.
    
    Args:
        results: List of calculation results with confidence_factors attribute
    
    Returns:
        Deduplicated list of all confidence factors
    """
    all_factors = []
    seen = set()
    
    for result in results:
        if hasattr(result, "confidence_factors"):
            for factor in result.confidence_factors:
                key = factor.get("factor", "")
                if key not in seen:
                    seen.add(key)
                    all_factors.append(factor)
    
    return all_factors
