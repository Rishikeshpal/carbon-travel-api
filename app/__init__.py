"""
Carbon Travel Intelligence API

A Carbon- & Resource-Aware Travel Intelligence Platform providing real-time 
carbon impact calculations, lower-impact alternatives, and CSRD-aligned ESG outputs.
"""

import os
from flask import Flask, render_template
from flask_cors import CORS


def create_app(config_name: str = "development") -> Flask:
    """Application factory pattern."""
    # Get the parent directory for templates
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Load configuration
    if config_name == "production":
        app.config.from_object("config.ProductionConfig")
    elif config_name == "testing":
        app.config.from_object("config.TestingConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")
    
    # Enable CORS
    CORS(app, resources={r"/v1/*": {"origins": "*"}})
    
    # Register blueprints
    from app.routes.assess import assess_bp
    from app.routes.alternatives import alternatives_bp
    from app.routes.factors import factors_bp
    from app.routes.reports import reports_bp
    from app.routes.trains import bp as trains_bp
    
    app.register_blueprint(assess_bp, url_prefix="/v1")
    app.register_blueprint(alternatives_bp, url_prefix="/v1")
    app.register_blueprint(factors_bp, url_prefix="/v1")
    app.register_blueprint(reports_bp, url_prefix="/v1")
    app.register_blueprint(trains_bp)
    
    # Root endpoint - serve the UI
    @app.route("/")
    def index():
        return render_template('index.html')
    
    # API info endpoint
    @app.route("/api")
    def api_info():
        return {
            "name": "Carbon Travel Intelligence API",
            "version": "1.0.0",
            "description": "Stripe for sustainability data in travel",
            "documentation": "/docs",
            "ui": "/",
            "endpoints": {
                "assess": "POST /v1/assess",
                "batch_assess": "POST /v1/assess/batch",
                "alternatives": "POST /v1/alternatives",
                "flight_factors": "GET /v1/factors/flights",
                "hotel_factors": "GET /v1/factors/hotels",
                "esg_report": "POST /v1/reports/esg",
                "train_search": "GET /v1/trains/search",
                "train_compare": "GET /v1/trains/compare",
                "train_routes": "GET /v1/trains/routes"
            }
        }
    
    # Health check
    @app.route("/health")
    def health():
        return {"status": "healthy", "version": "1.0.0"}
    
    return app
