# ============================================
# astro-service/app/config.py
# ============================================
"""
Configuration management for Astro Service.
Loads settings from environment variables with validation.
"""

import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator, field_validator


# ============================================
# Base Configuration
# ============================================

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ============================================
    # Application Settings
    # ============================================
    APP_NAME: str = Field(
        default="Singularity Astro Service",
        description="Application name"
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )
    APP_ENV: str = Field(
        default="development",
        description="Environment (development, staging, production)"
    )
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    # ============================================
    # Server Settings
    # ============================================
    HOST: str = Field(
        default="0.0.0.0",
        description="Server host"
    )
    PORT: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port"
    )
    RELOAD: bool = Field(
        default=False,
        description="Enable auto-reload (development only)"
    )
    WORKERS: int = Field(
        default=1,
        ge=1,
        le=16,
        description="Number of worker processes"
    )
    
    # ============================================
    # API Settings
    # ============================================
    API_PREFIX: str = Field(
        default="/api/v1",
        description="API route prefix"
    )
    API_KEY: str = Field(
        default="dev-key-change-in-production",
        description="API key for authentication"
    )
    SECRET_KEY: str = Field(
        default="super-secret-key-change-in-production",
        min_length=32,
        description="Secret key for JWT/sessions"
    )
    DISABLE_AUTH: bool = Field(
        default=False,
        description="Disable API authentication (development only)"
    )
    
    # ============================================
    # CORS Settings
    # ============================================
    CORS_ENABLED: bool = Field(
        default=True,
        description="Enable CORS"
    )
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    CORS_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed HTTP methods"
    )
    CORS_HEADERS: List[str] = Field(
        default=["*"],
        description="Allowed headers"
    )
    CORS_CREDENTIALS: bool = Field(
        default=True,
        description="Allow credentials"
    )
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # ============================================
    # Redis Cache Settings
    # ============================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    REDIS_DB: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis database number"
    )
    CACHE_ENABLED: bool = Field(
        default=True,
        description="Enable caching"
    )
    CACHE_TTL: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Default cache TTL in seconds"
    )
    PREDICTION_CACHE_TTL: int = Field(
        default=3600,
        description="Prediction cache TTL in seconds"
    )
    TLE_CACHE_TTL: int = Field(
        default=21600,  # 6 hours
        description="TLE cache TTL in seconds"
    )
    
    # ============================================
    # Logging Settings
    # ============================================
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    LOG_FILE: Optional[str] = Field(
        default=None,
        description="Log file path (None = console only)"
    )
    JSON_LOGS: bool = Field(
        default=False,
        description="Use JSON format for logs"
    )
    VERBOSE: bool = Field(
        default=False,
        description="Enable verbose logging"
    )
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v_upper
    
    # ============================================
    # Astronomy Settings
    # ============================================
    MIN_ELEVATION: float = Field(
        default=10.0,
        ge=0,
        le=90,
        description="Minimum satellite elevation in degrees"
    )
    MAX_PREDICTION_DAYS: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Maximum days ahead for predictions"
    )
    DEFAULT_ELEVATION_M: float = Field(
        default=0.0,
        ge=0,
        le=10000,
        description="Default observer elevation in meters"
    )
    SUN_ALTITUDE_THRESHOLD: float = Field(
        default=-12.0,
        ge=-18,
        le=0,
        description="Sun altitude threshold for darkness (degrees)"
    )
    
    # ============================================
    # TLE Data Sources
    # ============================================
    CELESTRAK_BASE_URL: str = Field(
        default="https://celestrak.org",
        description="Celestrak base URL"
    )
    TLE_UPDATE_INTERVAL_HOURS: int = Field(
        default=6,
        ge=1,
        le=24,
        description="TLE update interval in hours"
    )
    TLE_FETCH_TIMEOUT: int = Field(
        default=30,
        ge=5,
        le=120,
        description="TLE fetch timeout in seconds"
    )
    
    # Optional: Space-Track.org credentials
    SPACETRACK_USERNAME: Optional[str] = Field(
        default=None,
        description="Space-Track.org username"
    )
    SPACETRACK_PASSWORD: Optional[str] = Field(
        default=None,
        description="Space-Track.org password"
    )
    
    # ============================================
    # Weather API Settings (Optional)
    # ============================================
    OPENWEATHER_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenWeatherMap API key"
    )
    WEATHERAPI_KEY: Optional[str] = Field(
        default=None,
        description="WeatherAPI.com API key"
    )
    WEATHER_ENABLED: bool = Field(
        default=False,
        description="Enable weather API integration"
    )
    WEATHER_CACHE_TTL: int = Field(
        default=3600,
        description="Weather data cache TTL in seconds"
    )
    
    # ============================================
    # Rate Limiting Settings
    # ============================================
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default=100,
        ge=1,
        description="Max requests per window"
    )
    RATE_LIMIT_WINDOW: int = Field(
        default=3600,
        ge=60,
        description="Rate limit window in seconds"
    )
    RATE_LIMIT_STORAGE: str = Field(
        default="redis",
        description="Rate limit storage backend (redis, memory)"
    )
    
    # ============================================
    # Monitoring & Metrics
    # ============================================
    METRICS_ENABLED: bool = Field(
        default=True,
        description="Enable Prometheus metrics"
    )
    METRICS_PORT: int = Field(
        default=9090,
        ge=1,
        le=65535,
        description="Metrics endpoint port"
    )
    SENTRY_DSN: Optional[str] = Field(
        default=None,
        description="Sentry DSN for error tracking"
    )
    SENTRY_TRACES_SAMPLE_RATE: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Sentry traces sample rate"
    )
    
    # ============================================
    # Performance Settings
    # ============================================
    MAX_CONCURRENT_PREDICTIONS: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Max concurrent predictions"
    )
    REQUEST_TIMEOUT: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Request timeout in seconds"
    )
    ENABLE_PROFILING: bool = Field(
        default=False,
        description="Enable performance profiling"
    )
    
    # ============================================
    # Data Paths
    # ============================================
    DATA_DIR: Path = Field(
        default=Path("./data"),
        description="Data storage directory"
    )
    TLE_CACHE_DIR: Path = Field(
        default=Path("./data/tle-cache"),
        description="TLE cache directory"
    )
    LIGHT_POLLUTION_DATA_PATH: Optional[Path] = Field(
        default=None,
        description="Path to light pollution dataset"
    )
    
    @field_validator('DATA_DIR', 'TLE_CACHE_DIR', mode='before')
    @classmethod
    def parse_path(cls, v):
        """Convert string to Path."""
        if isinstance(v, str):
            return Path(v)
        return v
    
    # ============================================
    # Feature Flags
    # ============================================
    ENABLE_MOON_CALCULATIONS: bool = Field(
        default=True,
        description="Enable moon position calculations"
    )
    ENABLE_AIRMASS_CALCULATIONS: bool = Field(
        default=True,
        description="Enable atmospheric airmass calculations"
    )
    ENABLE_WEATHER_INTEGRATION: bool = Field(
        default=False,
        description="Enable weather API integration"
    )
    ENABLE_LIGHT_POLLUTION: bool = Field(
        default=True,
        description="Enable light pollution calculations"
    )
    
    # ============================================
    # Development Settings
    # ============================================
    USE_MOCK_DATA: bool = Field(
        default=False,
        description="Use mock data for testing"
    )
    MOCK_TLE_ENABLED: bool = Field(
        default=False,
        description="Use mock TLE data"
    )
    SKIP_VALIDATION: bool = Field(
        default=False,
        description="Skip input validation (testing only)"
    )
    
    # ============================================
    # Pydantic Configuration
    # ============================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # ============================================
    # Computed Properties
    # ============================================
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.APP_ENV.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.APP_ENV.lower() == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in test mode."""
        return self.APP_ENV.lower() == "test"
    
    @property
    def redis_url_full(self) -> str:
        """Get full Redis URL with database."""
        if self.REDIS_DB != 0:
            return f"{self.REDIS_URL}/{self.REDIS_DB}"
        return self.REDIS_URL
    
    @property
    def openapi_url(self) -> str:
        """Get OpenAPI schema URL."""
        return f"{self.API_PREFIX}/openapi.json" if not self.is_production else None
    
    @property
    def docs_url(self) -> Optional[str]:
        """Get Swagger UI docs URL."""
        return f"{self.API_PREFIX}/docs" if not self.is_production else None
    
    @property
    def redoc_url(self) -> Optional[str]:
        """Get ReDoc URL."""
        return f"{self.API_PREFIX}/redoc" if not self.is_production else None
    
    # ============================================
    # Validation Methods
    # ============================================
    def validate_settings(self) -> List[str]:
        """
        Validate settings and return list of warnings.
        
        Returns:
            List of warning messages
        """
        warnings = []
        
        # Production checks
        if self.is_production:
            if self.DEBUG:
                warnings.append("⚠️  DEBUG is enabled in production")
            
            if self.API_KEY == "dev-key-change-in-production":
                warnings.append("⚠️  Using default API key in production")
            
            if self.SECRET_KEY == "super-secret-key-change-in-production":
                warnings.append("⚠️  Using default SECRET_KEY in production")
            
            if self.DISABLE_AUTH:
                warnings.append("⚠️  Authentication is disabled in production")
            
            if not self.RATE_LIMIT_ENABLED:
                warnings.append("⚠️  Rate limiting is disabled in production")
            
            if not self.CACHE_ENABLED:
                warnings.append("⚠️  Caching is disabled in production")
        
        # Redis check
        if self.CACHE_ENABLED and not self.REDIS_URL:
            warnings.append("⚠️  Caching enabled but no Redis URL configured")
        
        # Weather API check
        if self.WEATHER_ENABLED and not (self.OPENWEATHER_API_KEY or self.WEATHERAPI_KEY):
            warnings.append("⚠️  Weather integration enabled but no API key configured")
        
        # Sentry check
        if self.is_production and not self.SENTRY_DSN:
            warnings.append("ℹ️  No Sentry DSN configured for error tracking")
        
        return warnings
    
    def create_data_directories(self):
        """Create required data directories."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.TLE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive values)."""
        sensitive_keys = [
            'API_KEY', 'SECRET_KEY', 'SPACETRACK_PASSWORD',
            'OPENWEATHER_API_KEY', 'WEATHERAPI_KEY', 'SENTRY_DSN'
        ]
        
        result = {}
        for key, value in self.model_dump().items():
            if key in sensitive_keys:
                result[key] = "***" if value else None
            else:
                result[key] = value
        
        return result
    
    def print_settings(self):
        """Print settings summary (for startup logs)."""
        print("\n" + "=" * 60)
        print(f"🚀 {self.APP_NAME} v{self.APP_VERSION}")
        print("=" * 60)
        print(f"Environment:        {self.APP_ENV}")
        print(f"Debug Mode:         {self.DEBUG}")
        print(f"Server:             {self.HOST}:{self.PORT}")
        print(f"API Prefix:         {self.API_PREFIX}")
        print(f"CORS Enabled:       {self.CORS_ENABLED}")
        print(f"Cache Enabled:      {self.CACHE_ENABLED}")
        print(f"Rate Limiting:      {self.RATE_LIMIT_ENABLED}")
        print(f"Weather API:        {self.WEATHER_ENABLED}")
        print(f"Metrics:            {self.METRICS_ENABLED}")
        print(f"Log Level:          {self.LOG_LEVEL}")
        print("=" * 60 + "\n")
        
        # Print warnings
        warnings = self.validate_settings()
        if warnings:
            print("⚠️  Configuration Warnings:")
            for warning in warnings:
                print(f"   {warning}")
            print()


# ============================================
# Configuration Presets
# ============================================

class DevelopmentSettings(Settings):
    """Development environment settings."""
    APP_ENV: str = "development"
    DEBUG: bool = True
    RELOAD: bool = True
    LOG_LEVEL: str = "DEBUG"
    VERBOSE: bool = True
    DISABLE_AUTH: bool = True
    RATE_LIMIT_ENABLED: bool = False
    JSON_LOGS: bool = False


class ProductionSettings(Settings):
    """Production environment settings."""
    APP_ENV: str = "production"
    DEBUG: bool = False
    RELOAD: bool = False
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True
    DISABLE_AUTH: bool = False
    RATE_LIMIT_ENABLED: bool = True
    WORKERS: int = 4


class TestSettings(Settings):
    """Test environment settings."""
    APP_ENV: str = "test"
    DEBUG: bool = True
    LOG_LEVEL: str = "WARNING"
    USE_MOCK_DATA: bool = True
    MOCK_TLE_ENABLED: bool = True
    CACHE_ENABLED: bool = False
    RATE_LIMIT_ENABLED: bool = False
    DISABLE_AUTH: bool = True


# ============================================
# Settings Factory
# ============================================

def get_settings_class(env: Optional[str] = None) -> type[Settings]:
    """
    Get settings class based on environment.
    
    Args:
        env: Environment name (development, production, test)
    
    Returns:
        Settings class
    """
    env = env or os.getenv("APP_ENV", "development")
    env_lower = env.lower()
    
    if env_lower == "production":
        return ProductionSettings
    elif env_lower == "test":
        return TestSettings
    else:
        return DevelopmentSettings


@lru_cache()
def get_settings(env: Optional[str] = None) -> Settings:
    """
    Get cached settings instance.
    
    Args:
        env: Environment name (development, production, test)
    
    Returns:
        Settings instance
    
    Example:
        settings = get_settings()
        print(settings.APP_NAME)
    """
    settings_class = get_settings_class(env)
    settings = settings_class()
    
    # Create required directories
    settings.create_data_directories()
    
    return settings


# ============================================
# Convenience Functions
# ============================================

def reload_settings():
    """Clear cached settings and reload."""
    get_settings.cache_clear()
    return get_settings()


def get_cors_config() -> Dict[str, Any]:
    """Get CORS configuration for FastAPI."""
    settings = get_settings()
    
    if not settings.CORS_ENABLED:
        return {}
    
    return {
        "allow_origins": settings.CORS_ORIGINS,
        "allow_credentials": settings.CORS_CREDENTIALS,
        "allow_methods": settings.CORS_METHODS,
        "allow_headers": settings.CORS_HEADERS,
    }


def get_redis_config() -> Dict[str, Any]:
    """Get Redis configuration."""
    settings = get_settings()
    
    return {
        "url": settings.redis_url_full,
        "encoding": "utf-8",
        "decode_responses": True,
        "socket_connect_timeout": 5
    }


# ============================================
# Module exports
# ============================================

__all__ = [
    "Settings",
    "DevelopmentSettings",
    "ProductionSettings",
    "TestSettings",
    "get_settings",
    "reload_settings",
    "get_cors_config",
    "get_redis_config"
]


# ============================================
# CLI for testing configuration
# ============================================

if __name__ == "__main__":
    """Test configuration loading."""
    import sys
    
    # Load settings
    env = sys.argv[1] if len(sys.argv) > 1 else None
    settings = get_settings(env)
    
    # Print settings
    settings.print_settings()
    
    # Validate
    warnings = settings.validate_settings()
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("✅ No configuration warnings")
    
    # Print full config (safe)
    print("\nFull Configuration:")
    import json
    print(json.dumps(settings.to_dict(), indent=2, default=str))