"""Application configuration."""

import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
    API_KEY_HEADER = "X-API-Key"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 1000
    
    # Emission factor versions
    EMISSION_FACTORS_VERSION = "2024.2"
    
    # Radiative forcing multiplier for flights
    RADIATIVE_FORCING_MULTIPLIER = 1.9


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    REQUIRE_API_KEY = False  # Disable for local development


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    REQUIRE_API_KEY = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    REQUIRE_API_KEY = True
    SECRET_KEY = os.environ.get("SECRET_KEY")  # Must be set in production
