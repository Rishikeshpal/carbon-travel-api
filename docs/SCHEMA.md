# API Schema Documentation

Detailed documentation of all request/response schemas for the Carbon Travel Intelligence API.

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Request Schemas](#request-schemas)
3. [Response Schemas](#response-schemas)
4. [Emission Factors](#emission-factors)
5. [Error Handling](#error-handling)

---

## Core Concepts

### Emissions Unit

All emissions are reported in **kg CO₂e** (kilograms of CO₂ equivalent), which includes:
- CO₂ (carbon dioxide)
- CH₄ (methane) — converted to CO₂e
- N₂O (nitrous oxide) — converted to CO₂e

### Confidence Scoring

Every assessment includes a confidence score indicating data quality:

| Level | Score Range | Meaning |
|-------|-------------|---------|
| High | 0.80 - 1.00 | Based on measured, specific data |
| Medium | 0.60 - 0.79 | Mix of specific and estimated data |
| Low | 0.00 - 0.59 | Primarily using defaults |

### Segment Types

| Type | Description | MVP Status |
|------|-------------|------------|
| `flight` | Commercial aviation | ✅ Supported |
| `hotel` | Accommodation | ✅ Supported |
| `train` | Rail transport | ✅ In alternatives |
| `bus` | Coach/bus transport | 🔜 v2 |
| `car` | Ground vehicle | 🔜 v2 |

---

## Request Schemas

### ItineraryRequest

The primary request object for carbon assessment.

```typescript
interface ItineraryRequest {
  // Client-provided unique identifier (optional)
  trip_id?: string;
  
  // Number of travelers (emissions multiplied)
  traveler_count?: number; // default: 1, max: 500
  
  // Travel segments (required, 1-50 segments)
  segments: (FlightSegment | HotelSegment)[];
  
  // Assessment options
  options?: AssessmentOptions;
}
```

### FlightSegment

```typescript
interface FlightSegment {
  // Discriminator
  type: "flight";
  
  // IATA airport codes (required)
  origin: string;      // 3 chars, e.g., "LHR"
  destination: string; // 3 chars, e.g., "CDG"
  
  // Date/time
  departure_date: string; // ISO 8601 date, e.g., "2025-03-15"
  departure_time?: string; // Optional, for grid-aware calcs
  
  // Flight details
  cabin_class?: "economy" | "premium_economy" | "business" | "first";
  carrier_code?: string; // 2-char IATA airline code
  flight_number?: string; // For specific aircraft lookup
  
  // Flag for return legs
  is_return?: boolean;
}
```

**Cabin Class Multipliers:**

| Class | Multiplier | Rationale |
|-------|------------|-----------|
| Economy | 1.0x | Baseline |
| Premium Economy | 1.5x | ~50% more space |
| Business | 3.0x | ~3x floor space |
| First | 4.0x | ~4x floor space |

### HotelSegment

```typescript
interface HotelSegment {
  // Discriminator
  type: "hotel";
  
  // Location (required)
  location: {
    city?: string;
    country_code: string; // ISO 3166-1 alpha-2
    coordinates?: {
      latitude: number;
      longitude: number;
    };
  };
  
  // Dates
  check_in: string;  // ISO 8601 date
  check_out: string; // ISO 8601 date
  
  // Hotel details
  star_rating?: 1 | 2 | 3 | 4 | 5;
  hotel_chain?: string; // For chain-specific data
  room_count?: number;  // default: 1
  sustainability_certified?: boolean;
}
```

**Star Rating Impact:**

| Rating | kWh/room/night | Rationale |
|--------|----------------|-----------|
| 1-star | 25 kWh | Basic amenities |
| 2-star | 30 kWh | Standard amenities |
| 3-star | 40 kWh | Air conditioning, minibar |
| 4-star | 55 kWh | Spa, restaurant, gym |
| 5-star | 80 kWh | Luxury amenities, larger rooms |

### AssessmentOptions

```typescript
interface AssessmentOptions {
  // Include lower-impact alternatives
  include_alternatives?: boolean; // default: false
  
  // Number of alternatives (if included)
  alternative_count?: number; // 1-10, default: 3
  
  // Calculation methodology
  calculation_method?: "standard" | "detailed" | "conservative";
  // - standard: ICAO + DEFRA defaults
  // - detailed: Airline/hotel specific where available
  // - conservative: Upper-bound for cautious reporting
  
  // Include methodology notes
  include_methodology?: boolean; // default: false
}
```

---

## Response Schemas

### AssessmentResponse

The primary response object containing emissions data.

```typescript
interface AssessmentResponse {
  // Unique assessment identifier
  assessment_id: string; // UUID format
  
  // Echo of client trip_id
  trip_id?: string;
  
  // Total emissions summary
  total_emissions: EmissionsTotal;
  
  // Data quality indicator
  confidence_score: ConfidenceScore;
  
  // Per-segment breakdown
  segments: SegmentEmissions[];
  
  // Optional: lower-impact alternatives
  lower_impact_alternatives?: Alternative[];
  
  // Optional: methodology details
  methodology?: Methodology;
  
  // Timestamps
  created_at: string; // ISO 8601 datetime
  expires_at: string; // When factors may update
}
```

### EmissionsTotal

```typescript
interface EmissionsTotal {
  // Total CO₂ equivalent
  co2e_kg: number;
  unit: "kg_co2e";
  
  // Category breakdown
  breakdown: {
    flights_kg: number;
    hotels_kg: number;
    ground_transport_kg?: number; // Future
  };
  
  // Per-traveler emissions
  per_traveler_kg: number;
  
  // Human-readable equivalents
  equivalent: {
    trees_to_offset: number;    // Trees absorbing for 1 year
    driving_km: number;          // Km in average ICE car
    streaming_hours: number;     // Hours of video streaming
  };
}
```

### ConfidenceScore

```typescript
interface ConfidenceScore {
  // Numeric score (0-1)
  score: number;
  
  // Categorical level
  level: "high" | "medium" | "low";
  
  // Contributing factors
  factors: Array<{
    factor: string;              // Factor name
    impact: "positive" | "negative" | "neutral";
    description: string;         // Human-readable explanation
  }>;
}
```

### SegmentEmissions

```typescript
interface SegmentEmissions {
  // Index in original request
  segment_index: number;
  
  // Segment type
  type: "flight" | "hotel";
  
  // Emissions for this segment
  emissions_kg: number;
  
  // Type-specific details
  details: FlightEmissionDetails | HotelEmissionDetails;
}
```

### FlightEmissionDetails

```typescript
interface FlightEmissionDetails {
  // Route info
  distance_km: number;
  haul_type: "short" | "medium" | "long";
  // short: <1500km, medium: 1500-4000km, long: >4000km
  
  // Calculation factors
  radiative_forcing_multiplier: number; // Typically 1.9
  fuel_burn_kg: number;
  
  // Aircraft info (if available)
  aircraft_type?: string;
  load_factor: number; // Assumed passenger load
  
  // Data source
  emission_factor_source: string;
}
```

### HotelEmissionDetails

```typescript
interface HotelEmissionDetails {
  // Stay info
  nights: number;
  emissions_per_night_kg: number;
  
  // Grid data
  grid_carbon_intensity: {
    value: number;        // gCO₂/kWh
    source: string;       // Data source
    country: string;      // Country code
  };
  
  // Energy consumption
  energy_consumption_kwh: number;
  
  // Data source
  emission_factor_source: string;
}
```

### Alternative

```typescript
interface Alternative {
  // Unique ID for this alternative
  alternative_id: string;
  
  // Emissions for alternative itinerary
  total_emissions: EmissionsTotal;
  
  // Savings compared to original
  savings: {
    absolute_kg: number;  // CO₂e saved
    percentage: number;   // Percentage reduction
    label: string;        // Human-readable label
  };
  
  // Replacement segments
  segments: AlternativeSegment[];
  
  // Tradeoff analysis
  tradeoffs: {
    time_difference_minutes: number;  // Positive = longer
    estimated_cost_difference_eur: number;
    comfort_score: number; // 0-5
  };
  
  // Why this is recommended
  recommendation_reason: string;
}
```

---

## Emission Factors

### Flight Emission Factors

Based on ICAO methodology with DEFRA 2024 factors:

| Haul Type | Distance | kg CO₂e/km (Economy) |
|-----------|----------|---------------------|
| Short | <1,500 km | 0.255 |
| Medium | 1,500-4,000 km | 0.156 |
| Long | >4,000 km | 0.150 |

**Radiative Forcing:**
All flight emissions include a 1.9x multiplier for radiative forcing (RF), accounting for high-altitude effects including contrails and NOx emissions.

**Cabin Class:**
Multiply by cabin class factor (Economy: 1.0, Premium: 1.5, Business: 3.0, First: 4.0).

### Hotel Emission Factors

Energy consumption by star rating:

| Rating | kWh/room/night |
|--------|----------------|
| 1-star | 25 |
| 2-star | 30 |
| 3-star | 40 |
| 4-star | 55 |
| 5-star | 80 |

Emissions = kWh × Grid Carbon Intensity (g CO₂/kWh) / 1000

### Regional Grid Carbon Intensity (Selected)

| Country | Grid Intensity (g CO₂/kWh) | Source |
|---------|---------------------------|--------|
| France | 56 | ENTSO-E 2024 |
| Sweden | 41 | ENTSO-E 2024 |
| UK | 198 | National Grid 2024 |
| Germany | 366 | ENTSO-E 2024 |
| Poland | 773 | ENTSO-E 2024 |
| USA (avg) | 386 | EPA eGRID 2024 |
| China (avg) | 555 | IEA 2024 |

### Train Emission Factors

| Train Type | kg CO₂/passenger-km |
|------------|---------------------|
| Eurostar | 0.004 |
| TGV (France) | 0.003 |
| ICE (Germany) | 0.032 |
| UK Rail (avg) | 0.035 |
| Intercity (diesel) | 0.089 |

---

## Error Handling

### Error Response Format

```typescript
interface ErrorResponse {
  code: string;           // Machine-readable error code
  message: string;        // Human-readable message
  field?: string;         // Field that caused error (if applicable)
  details?: object;       // Additional error context
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request body failed validation |
| `INVALID_AIRPORT_CODE` | 400 | Unknown IATA airport code |
| `INVALID_DATE` | 400 | Date format invalid or in past |
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `ROUTE_NOT_FOUND` | 422 | No route between airports |
| `COUNTRY_NOT_SUPPORTED` | 422 | Country code not in database |
| `INTERNAL_ERROR` | 500 | Server error |

### Example Error Response

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid request body",
  "details": {
    "errors": [
      {
        "field": "segments[0].origin",
        "message": "Airport code 'XYZ' not found in IATA database"
      },
      {
        "field": "segments[1].check_in",
        "message": "Check-in date must be before check-out date"
      }
    ]
  }
}
```

---

## Rate Limits

| Plan | Requests/minute | Requests/day |
|------|-----------------|--------------|
| Free | 60 | 1,000 |
| Starter | 300 | 10,000 |
| Professional | 1,000 | 100,000 |
| Enterprise | 10,000 | Unlimited |

Rate limit headers returned:
- `X-RateLimit-Limit`: Requests per minute allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets
