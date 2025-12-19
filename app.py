#!/usr/bin/env python3
"""
Carbon Travel Intelligence API

Run with:
    python app.py                    # Development server
    gunicorn app:app -b 0.0.0.0:8080 # Production
"""

import os
from app import create_app

# Create app instance
config = os.environ.get("FLASK_ENV", "development")
app = create_app(config)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug = config == "development"
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🌱 Carbon Travel Intelligence API                            ║
║     "Stripe for sustainability data in travel"               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Server running at: http://localhost:{port}                   ║
║  Environment: {config:<12}                                    ║
║                                                              ║
║  Endpoints:                                                  ║
║    POST /v1/assess           → Calculate emissions           ║
║    POST /v1/assess/batch     → Batch assessment              ║
║    POST /v1/alternatives     → Find lower-impact options     ║
║    GET  /v1/factors/flights  → Flight emission factors       ║
║    GET  /v1/factors/hotels   → Hotel factors by region       ║
║    GET  /v1/factors/trains   → Train emission factors        ║
║    POST /v1/reports/esg      → Generate ESG report           ║
║                                                              ║
║  Utility endpoints:                                          ║
║    GET  /                    → API info                      ║
║    GET  /health              → Health check                  ║
║    GET  /v1/factors/airports → List airports                 ║
║    GET  /v1/factors/distance → Calculate route distance      ║
║                                                              ║
║  Press Ctrl+C to stop                                        ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
