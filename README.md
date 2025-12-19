# 🌍 Carbon Travel Intelligence API

> **"Stripe for sustainability data in travel"**

A Carbon- & Resource-Aware Travel Intelligence Platform providing real-time carbon impact calculations for flights, hotels, and ground transport with lower-impact alternatives.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| ✈️ **Flight Emissions** | Short/long haul, cabin class, return trips |
| 🏨 **Hotel Emissions** | Star rating, energy consumption, regional grid intensity |
| 🍳 **Breakfast Impact** | Continental, buffet, full English, vegan options |
| 🚕 **Ground Transport** | Airport transfers, Uber, taxi, public transit |
| 🌿 **Alternatives Engine** | Train vs flight, eco-hotel suggestions |
| 📊 **Confidence Scoring** | Data quality transparency |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Local Development

```bash
# 1. Clone and navigate
cd carbon-travel-api

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python app.py
```

The app runs at **http://localhost:8080**

### Test the API

```bash
curl -X POST http://localhost:8080/v1/assess \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "test_trip",
    "traveler_count": 1,
    "segments": [
      {"type": "flight", "origin": "LHR", "destination": "CDG", "departure_date": "2025-04-01", "cabin_class": "economy"}
    ]
  }'
```

---

## 🖥️ Web UI

Access the interactive calculator at **http://localhost:8080**

Features:
- Quick route buttons (Dublin→Singapore, London→Paris, etc.)
- Optional hotel with breakfast selection
- Airport transfer options (Uber, taxi, metro)
- City transport during stay
- Real-time emission breakdown

---

## 📦 Deployment

### Option 1: Docker (Recommended)

```bash
# Build the image
docker build -t carbon-travel-api .

# Run the container
docker run -d -p 8080:8080 --name carbon-api carbon-travel-api

# Verify it's running
curl http://localhost:8080/health
```

### Option 2: Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

Then run:
```bash
docker-compose up -d
```

### Option 3: Cloud Platforms

#### AWS (Elastic Beanstalk)
```bash
# Install EB CLI
pip install awsebcli

# Initialize and deploy
eb init -p python-3.11 carbon-travel-api
eb create production
eb deploy
```

#### Google Cloud Run
```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/carbon-travel-api

# Deploy
gcloud run deploy carbon-travel-api \
  --image gcr.io/PROJECT_ID/carbon-travel-api \
  --port 8080 \
  --allow-unauthenticated
```

#### Fly.io
```bash
# Install flyctl and authenticate
fly auth login

# Launch (creates fly.toml automatically)
fly launch

# Deploy
fly deploy
```

#### Railway / Render
1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn --bind 0.0.0.0:$PORT app:create_app()`
4. Deploy

### Option 4: Manual VPS/Server

```bash
# SSH to your server
ssh user@your-server

# Clone the repository
git clone <your-repo-url> carbon-travel-api
cd carbon-travel-api

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with gunicorn (production)
gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 4 "app:create_app()"

# Or use systemd for auto-restart (create /etc/systemd/system/carbon-api.service)
```

Example systemd service file:
```ini
[Unit]
Description=Carbon Travel API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/carbon-travel-api
Environment="PATH=/opt/carbon-travel-api/venv/bin"
ExecStart=/opt/carbon-travel-api/venv/bin/gunicorn --bind 0.0.0.0:8080 --workers 2 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable carbon-api
sudo systemctl start carbon-api
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/health` | GET | Health check |
| `/v1/assess` | POST | Calculate trip emissions |
| `/v1/assess/batch` | POST | Batch assessment (up to 100 trips) |
| `/v1/alternatives` | POST | Find greener alternatives |
| `/v1/factors/flights` | GET | Flight emission factors |
| `/v1/factors/hotels` | GET | Hotel emission factors |
| `/v1/factors/distance` | GET | Calculate route distance |
| `/v1/factors/grid-intensity` | GET | Grid carbon intensity by region |

---

## 📊 Emission Factors

### Flights (kg CO₂e per km per passenger)

| Haul Type | Economy | Premium | Business | First |
|-----------|---------|---------|----------|-------|
| Short (<1500km) | 0.156 | 0.195 | 0.280 | 0.390 |
| Medium (1500-4000km) | 0.130 | 0.163 | 0.234 | 0.325 |
| Long (>4000km) | 0.111 | 0.139 | 0.200 | 0.278 |

### Ground Transport (kg CO₂e per km)

| Vehicle | Factor |
|---------|--------|
| Regular Taxi | 0.149 |
| Uber/Bolt | 0.121 |
| Electric Uber | 0.048 |
| Local Bus | 0.089 |
| Metro/Train | 0.029 |

### Breakfast (kg CO₂e per person)

| Type | Factor |
|------|--------|
| Continental | 0.8 |
| Buffet | 2.2 |
| Full English | 2.8 |
| Vegan | 0.5 |

---

## 📁 Project Structure

```
carbon-travel-api/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes/
│   │   ├── assess.py        # /v1/assess endpoints
│   │   ├── alternatives.py  # /v1/alternatives endpoints
│   │   ├── factors.py       # /v1/factors endpoints
│   │   └── reports.py       # /v1/reports endpoints
│   ├── services/
│   │   ├── flight_calculator.py
│   │   ├── hotel_calculator.py
│   │   ├── alternatives_engine.py
│   │   └── confidence_scorer.py
│   └── data/
│       ├── airports.py         # Airport coordinates
│       ├── emission_factors.py # CO₂e factors
│       ├── grid_intensity.py   # Regional grid data
│       └── transport_factors.py # Ground transport factors
├── templates/
│   └── index.html           # Web UI
├── docs/
│   ├── CASE_STUDY.md        # Example use case
│   └── SCHEMA.md            # API schema docs
├── examples/                # Sample requests
├── schemas/                 # JSON schemas
├── app.py                   # Entry point
├── config.py                # Configuration
├── requirements.txt         # Dependencies
├── Dockerfile               # Container build
└── README.md                # This file
```

---

## 🌍 Data Sources

- **ICAO Carbon Calculator** - Flight methodology
- **DEFRA 2024** - UK Government emission factors
- **ENTSO-E** - EU real-time grid intensity
- **Cornell HSBI** - Hotel energy benchmarks
- **UIC Railway Handbook** - Train emission factors

---

## 📄 License

Proprietary. All rights reserved.
