# 🌍 Carbon Travel Intelligence API

> **"Stripe for sustainability data in travel"**

A Carbon- & Resource-Aware Travel Intelligence Platform providing real-time carbon impact calculations for flights, hotels, ground transport, and European train alternatives.

---

## 📖 About

### The Problem

Travel accounts for **8% of global carbon emissions**, yet most travelers have no visibility into their environmental impact. With the EU's CSRD mandates requiring emissions disclosure, companies need accurate, auditable travel carbon data.

### The Solution

A **single API** to calculate complete trip carbon footprints:

- **Flights** — Origin/destination, cabin class, haul type
- **Hotels** — Star rating, regional grid intensity, breakfast emissions
- **Ground Transport** — Airport transfers, Uber, taxi, public transit
- **European Trains** — 19+ high-speed routes with real schedules, station info, and booking links

### Key Differentiators

| Feature | Description |
|---------|-------------|
| ✅ **EU-First** | Granular European grid carbon data (ENTSO-E) |
| ✅ **Audit-Ready** | CSRD-aligned methodology with confidence scoring |
| ✅ **Actionable** | Suggests lower-impact train alternatives |
| ✅ **Complete** | Flights + hotels + breakfast + transport + trains |
| ✅ **Bookable** | Direct links to Trainline, Omio, Eurostar, etc. |

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| ✈️ **Flight Emissions** | Short/long haul, cabin class, return trips |
| 🏨 **Hotel Emissions** | Star rating, energy use, grid intensity |
| 🍳 **Breakfast Impact** | Continental, buffet, full English, vegan |
| 🚕 **Ground Transport** | Airport transfers, Uber, taxi, metro |
| 🚂 **European Trains** | 19 routes with schedules & booking links |
| 🌿 **Alternatives** | Train vs flight comparisons |
| 📊 **Confidence Score** | Data quality transparency |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+

### Installation

```bash
cd carbon-travel-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Server runs at **http://localhost:8080**

### Test the API

```bash
# Health check
curl http://localhost:8080/health

# Calculate flight emissions
curl -X POST http://localhost:8080/v1/assess \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "test",
    "segments": [
      {"type": "flight", "origin": "LHR", "destination": "CDG", "departure_date": "2025-04-01", "cabin_class": "economy"}
    ]
  }'

# Compare train vs flight
curl "http://localhost:8080/v1/trains/compare?origin=LHR&destination=CDG"
```

---

## 🖥️ Web UI

Access the interactive calculator at **http://localhost:8080**

**Two tabs:**
1. **✈️ Flight Calculator** — Full trip with hotels, transfers, city transport
2. **🚂 European Trains** — Route finder with booking links

---

## 🔌 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/health` | GET | Health check |
| `/v1/assess` | POST | Calculate trip emissions |
| `/v1/assess/batch` | POST | Batch assessment |
| `/v1/alternatives` | POST | Find greener options |

### Train Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/trains/search` | GET | Search train routes |
| `/v1/trains/compare` | GET | Compare train vs flight |
| `/v1/trains/routes` | GET | List all train routes |
| `/v1/trains/book` | GET | Get booking URLs |

### Factor Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/factors/flights` | GET | Flight emission factors |
| `/v1/factors/hotels` | GET | Hotel emission factors |
| `/v1/factors/distance` | GET | Calculate route distance |

---

## 🚂 European Train Routes

### Supported Routes (19 total)

| Route | Operator | Duration | CO₂ Savings |
|-------|----------|----------|-------------|
| London → Paris | Eurostar | 2h 17m | **89%** |
| London → Amsterdam | Eurostar | 3h 48m | 85% |
| London → Brussels | Eurostar | 2h 00m | 88% |
| Paris → Amsterdam | Thalys | 3h 15m | 82% |
| Paris → Brussels | Thalys | 1h 22m | 90% |
| Frankfurt → Munich | ICE | 3h 15m | 75% |
| Madrid → Barcelona | AVE | 2h 35m | 80% |
| Rome → Milan | Frecciarossa | 2h 55m | 76% |

### Booking Platforms

| Platform | Deep Link | Description |
|----------|-----------|-------------|
| 🎫 **Trainline** | ✅ Yes | Pre-fills route & date |
| 🚂 **Omio** | ✅ Yes | Pre-fills route & date |
| ⭐ **Eurostar** | Direct | Official booking |
| 🌍 **Rail Europe** | Direct | 30+ countries |
| 🇫🇷 **SNCF Connect** | Direct | French TGV |
| 🇩🇪 **Deutsche Bahn** | Direct | German ICE |

---

## 📊 Emission Factors

### Flights (kg CO₂e per km per passenger)

| Haul | Economy | Business | First |
|------|---------|----------|-------|
| Short (<1500km) | 0.156 | 0.280 | 0.390 |
| Medium | 0.130 | 0.234 | 0.325 |
| Long (>4000km) | 0.111 | 0.200 | 0.278 |

### Ground Transport (kg CO₂e per km)

| Vehicle | Factor |
|---------|--------|
| Taxi | 0.149 |
| Uber/Bolt | 0.121 |
| Electric Uber | 0.048 |
| Metro | 0.029 |

### Breakfast (kg CO₂e per person)

| Type | Factor |
|------|--------|
| Continental | 0.8 |
| Buffet | 2.2 |
| Full English | 2.8 |
| Vegan | 0.5 |

---

## 📦 Deployment

### Docker

```bash
# Build
docker build -t carbon-travel-api .

# Run
docker run -d -p 8080:8080 carbon-travel-api

# Verify
curl http://localhost:8080/health
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8080:8080"
    restart: unless-stopped
```

### Cloud Platforms

**Google Cloud Run:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/carbon-travel-api
gcloud run deploy --image gcr.io/PROJECT_ID/carbon-travel-api --port 8080
```

**Fly.io:**
```bash
fly launch
fly deploy
```

---

## 📁 Project Structure

```
carbon-travel-api/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── data/
│   │   ├── airports.py       # Airport coordinates
│   │   ├── emission_factors.py
│   │   ├── grid_intensity.py
│   │   └── transport_factors.py
│   ├── routes/
│   │   ├── assess.py         # /v1/assess
│   │   ├── alternatives.py   # /v1/alternatives
│   │   ├── factors.py        # /v1/factors
│   │   ├── reports.py        # /v1/reports
│   │   └── trains.py         # /v1/trains
│   └── services/
│       ├── flight_calculator.py
│       ├── hotel_calculator.py
│       ├── train_service.py
│       ├── alternatives_engine.py
│       └── confidence_scorer.py
├── templates/
│   └── index.html            # Web UI
├── app.py                    # Entry point
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── Dockerfile                # Container build
├── .gitignore
└── .dockerignore
```

---

## 🌍 Data Sources

| Source | Usage |
|--------|-------|
| **ICAO** | Flight emission methodology |
| **DEFRA 2024** | UK Government emission factors |
| **ENTSO-E** | EU real-time grid intensity |
| **Cornell HSBI** | Hotel energy benchmarks |
| **UIC Railway Handbook** | Train emission factors |

---

## 📄 License

Proprietary. All rights reserved.
