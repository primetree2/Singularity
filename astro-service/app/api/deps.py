# ============================================
# astro-service/app/api/deps.py
# ============================================
"""
API dependencies and shared utilities.
Handles dependency injection, caching, authentication, etc.
"""

from typing import Optional, Generator
from functools import lru_cache
import redis.asyncio as redis
from fastapi import Depends, HTTPException, status, Header
import logging
import os

from app.core.visibility import VisibilityPredictor
from app.core.tle import TLEManager
from app.core.geometry import GeometryCalculator
from app.core.scoring import VisibilityScorer

logger = logging.getLogger(__name__)


# ============================================
# Configuration
# ============================================

class Settings:
    """Application settings loaded from environment."""
    
    def __init__(self):
        self.API_KEY = os.getenv("API_KEY", "dev-key-change-in-production")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.CACHE_TTL = int(os.getenv("PREDICTION_CACHE_TTL", "3600"))
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.MIN_ELEVATION = float(os.getenv("MIN_ELEVATION", "10.0"))
        self.MAX_PREDICTION_DAYS = int(os.getenv("MAX_PREDICTION_DAYS", "7"))
        
        # Rate limiting
        self.RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # seconds


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# ============================================
# Redis Cache
# ============================================

redis_client: Optional[redis.Redis] = None


async def get_redis() -> Optional[redis.Redis]:
    """Get Redis client for caching."""
    global redis_client
    
    settings = get_settings()
    
    if not settings.CACHE_ENABLED:
        return None
    
    if redis_client is None:
        try:
            redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Continuing without cache.")
            redis_client = None
    
    return redis_client


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


# ============================================
# Core Service Dependencies
# ============================================

# Global instances (singleton pattern)
_tle_manager: Optional[TLEManager] = None
_geometry_calculator: Optional[GeometryCalculator] = None
_visibility_scorer: Optional[VisibilityScorer] = None
_visibility_predictor: Optional[VisibilityPredictor] = None


def get_tle_manager() -> TLEManager:
    """Get TLE manager instance (singleton)."""
    global _tle_manager
    if _tle_manager is None:
        _tle_manager = TLEManager(cache_ttl_hours=6)
        logger.info("TLE Manager initialized")
    return _tle_manager


def get_geometry_calculator() -> GeometryCalculator:
    """Get geometry calculator instance (singleton)."""
    global _geometry_calculator
    if _geometry_calculator is None:
        _geometry_calculator = GeometryCalculator()
        logger.info("Geometry Calculator initialized")
    return _geometry_calculator


def get_visibility_scorer() -> VisibilityScorer:
    """Get visibility scorer instance (singleton)."""
    global _visibility_scorer
    if _visibility_scorer is None:
        _visibility_scorer = VisibilityScorer()
        logger.info("Visibility Scorer initialized")
    return _visibility_scorer


def get_visibility_predictor(
    tle_manager: TLEManager = Depends(get_tle_manager),
    geometry: GeometryCalculator = Depends(get_geometry_calculator),
    scorer: VisibilityScorer = Depends(get_visibility_scorer)
) -> VisibilityPredictor:
    """Get visibility predictor instance (singleton)."""
    global _visibility_predictor
    if _visibility_predictor is None:
        _visibility_predictor = VisibilityPredictor(
            tle_manager=tle_manager,
            geometry_calculator=geometry,
            scorer=scorer
        )
        logger.info("Visibility Predictor initialized")
    return _visibility_predictor


# ============================================
# Authentication
# ============================================

async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings)
) -> bool:
    """
    Verify API key from header.
    
    In development, this can be disabled.
    In production, always require valid API key.
    """
    # In development mode, allow requests without API key
    if settings.DEBUG and x_api_key is None:
        logger.warning("API key verification disabled (DEBUG mode)")
        return True
    
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header required"
        )
    
    if x_api_key != settings.API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return True


# ============================================
# Rate Limiting
# ============================================

async def check_rate_limit(
    client_id: str,
    redis_client: Optional[redis.Redis] = Depends(get_redis),
    settings: Settings = Depends(get_settings)
) -> bool:
    """
    Check rate limit for a client.
    
    Uses Redis to track requests per time window.
    Falls back to no rate limiting if Redis unavailable.
    """
    if not settings.RATE_LIMIT_ENABLED or redis_client is None:
        return True
    
    try:
        key = f"rate_limit:{client_id}"
        
        # Get current count
        current = await redis_client.get(key)
        
        if current is None:
            # First request in window
            await redis_client.setex(
                key,
                settings.RATE_LIMIT_WINDOW,
                1
            )
            return True
        
        current_count = int(current)
        
        if current_count >= settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW}s"
            )
        
        # Increment counter
        await redis_client.incr(key)
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        # Fail open - allow request if rate limiting fails
        return True


# ============================================
# Cache Helpers
# ============================================

async def get_cached_prediction(
    cache_key: str,
    redis_client: Optional[redis.Redis] = None
) -> Optional[dict]:
    """Get cached prediction from Redis."""
    if redis_client is None:
        return None
    
    try:
        cached = await redis_client.get(f"prediction:{cache_key}")
        if cached:
            import json
            return json.loads(cached)
    except Exception as e:
        logger.error(f"Cache get failed: {e}")
    
    return None


async def set_cached_prediction(
    cache_key: str,
    data: dict,
    ttl: int = 3600,
    redis_client: Optional[redis.Redis] = None
):
    """Cache prediction in Redis."""
    if redis_client is None:
        return
    
    try:
        import json
        await redis_client.setex(
            f"prediction:{cache_key}",
            ttl,
            json.dumps(data)
        )
    except Exception as e:
        logger.error(f"Cache set failed: {e}")


def generate_cache_key(*args) -> str:
    """Generate cache key from arguments."""
    import hashlib
    key_string = ":".join(str(arg) for arg in args)
    return hashlib.md5(key_string.encode()).hexdigest()


# ============================================
# Validation Helpers
# ============================================

def validate_coordinates(lat: float, lng: float):
    """Validate latitude and longitude."""
    if not (-90 <= lat <= 90):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid latitude: {lat}. Must be between -90 and 90"
        )
    
    if not (-180 <= lng <= 180):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid longitude: {lng}. Must be between -180 and 180"
        )


def validate_days_ahead(days: int, settings: Settings):
    """Validate days ahead parameter."""
    if days < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="days_ahead must be at least 1"
        )
    
    if days > settings.MAX_PREDICTION_DAYS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"days_ahead cannot exceed {settings.MAX_PREDICTION_DAYS}"
        )


# ============================================
# astro-service/app/api/routes/predictions.py
# ============================================
"""
Prediction endpoints for satellite visibility.
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
import logging

from app.api.deps import (
    get_visibility_predictor,
    verify_api_key,
    get_redis,
    get_settings,
    validate_coordinates,
    validate_days_ahead,
    get_cached_prediction,
    set_cached_prediction,
    generate_cache_key,
    Settings
)
from app.core.visibility import VisibilityPredictor
import redis.asyncio as redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predictions", tags=["predictions"])


# ============================================
# Request/Response Models
# ============================================

class PredictionRequest(BaseModel):
    """Request model for visibility prediction."""
    satellite_name: str = Field(..., description="Satellite name (e.g., 'ISS')")
    observer_lat: float = Field(..., ge=-90, le=90, description="Observer latitude")
    observer_lng: float = Field(..., ge=-180, le=180, description="Observer longitude")
    observer_elevation: float = Field(0, ge=0, le=10000, description="Elevation in meters")
    observation_time: Optional[datetime] = Field(None, description="Time to check (UTC). If null, uses current time")
    cloud_cover: float = Field(0, ge=0, le=100, description="Cloud coverage percentage")
    light_pollution: float = Field(0.5, ge=0, le=1, description="Light pollution index (0=dark, 1=bright)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "satellite_name": "ISS",
                "observer_lat": 40.7128,
                "observer_lng": -74.0060,
                "observer_elevation": 10,
                "cloud_cover": 20,
                "light_pollution": 0.7
            }
        }


class PassesRequest(BaseModel):
    """Request model for finding upcoming passes."""
    satellite_name: str = Field(..., description="Satellite name")
    observer_lat: float = Field(..., ge=-90, le=90)
    observer_lng: float = Field(..., ge=-180, le=180)
    days_ahead: int = Field(7, ge=1, le=14, description="Days to search ahead")
    min_score: float = Field(50, ge=0, le=100, description="Minimum visibility score")
    cloud_cover: float = Field(0, ge=0, le=100)
    light_pollution: float = Field(0.5, ge=0, le=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "satellite_name": "ISS",
                "observer_lat": 40.7128,
                "observer_lng": -74.0060,
                "days_ahead": 7,
                "min_score": 60,
                "light_pollution": 0.7
            }
        }


# ============================================
# Endpoints
# ============================================

@router.post("/predict")
async def predict_visibility(
    request: PredictionRequest,
    predictor: VisibilityPredictor = Depends(get_visibility_predictor),
    redis_client: Optional[redis.Redis] = Depends(get_redis),
    settings: Settings = Depends(get_settings),
    authenticated: bool = Depends(verify_api_key)
):
    """
    Predict satellite visibility at a specific time.
    
    Returns detailed visibility information including:
    - Satellite position (altitude, azimuth, distance)
    - Sun and moon positions
    - Visibility score (0-100) with component breakdown
    - Recommendation (visible/not visible)
    """
    try:
        # Validate coordinates
        validate_coordinates(request.observer_lat, request.observer_lng)
        
        # Use current time if not specified
        obs_time = request.observation_time or datetime.now(timezone.utc)
        
        # Generate cache key
        cache_key = generate_cache_key(
            request.satellite_name,
            request.observer_lat,
            request.observer_lng,
            obs_time.isoformat(),
            request.cloud_cover,
            request.light_pollution
        )
        
        # Check cache
        if settings.CACHE_ENABLED and redis_client:
            cached = await get_cached_prediction(cache_key, redis_client)
            if cached:
                logger.debug(f"Cache hit for prediction: {cache_key}")
                return cached
        
        # Calculate prediction
        result = await predictor.predict_satellite_visibility(
            satellite_name=request.satellite_name,
            observer_lat=request.observer_lat,
            observer_lng=request.observer_lng,
            observation_time=obs_time,
            observer_elevation=request.observer_elevation,
            cloud_cover=request.cloud_cover,
            light_pollution=request.light_pollution
        )
        
        # Cache result
        if settings.CACHE_ENABLED and redis_client and 'error' not in result:
            await set_cached_prediction(
                cache_key,
                result,
                ttl=settings.CACHE_TTL,
                redis_client=redis_client
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/passes")
async def find_upcoming_passes(
    request: PassesRequest,
    predictor: VisibilityPredictor = Depends(get_visibility_predictor),
    settings: Settings = Depends(get_settings),
    authenticated: bool = Depends(verify_api_key)
):
    """
    Find all upcoming visible passes for a satellite.
    
    Returns list of passes sorted by visibility score (best first).
    Each pass includes:
    - Rise, peak, and set times
    - Maximum altitude and azimuth
    - Duration
    - Visibility score and details
    - Sun/moon conditions
    """
    try:
        # Validate inputs
        validate_coordinates(request.observer_lat, request.observer_lng)
        validate_days_ahead(request.days_ahead, settings)
        
        # Find passes
        passes = await predictor.find_next_visible_passes(
            satellite_name=request.satellite_name,
            observer_lat=request.observer_lat,
            observer_lng=request.observer_lng,
            days_ahead=request.days_ahead,
            min_score=request.min_score,
            cloud_cover=request.cloud_cover,
            light_pollution=request.light_pollution
        )
        
        # Convert datetime objects to ISO strings
        for pass_info in passes:
            pass_info['rise'] = pass_info['rise'].isoformat()
            pass_info['peak'] = pass_info['peak'].isoformat()
            pass_info['set'] = pass_info['set'].isoformat()
        
        return {
            "satellite": request.satellite_name,
            "observer": {
                "latitude": request.observer_lat,
                "longitude": request.observer_lng
            },
            "search_criteria": {
                "days_ahead": request.days_ahead,
                "min_score": request.min_score
            },
            "total_passes": len(passes),
            "passes": passes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Passes search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Passes search failed: {str(e)}"
        )


@router.get("/current/{satellite_name}")
async def get_current_visibility(
    satellite_name: str,
    lat: float = Query(..., ge=-90, le=90, description="Observer latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Observer longitude"),
    cloud_cover: float = Query(0, ge=0, le=100),
    light_pollution: float = Query(0.5, ge=0, le=1),
    predictor: VisibilityPredictor = Depends(get_visibility_predictor),
    authenticated: bool = Depends(verify_api_key)
):
    """
    Get current visibility for a satellite right now (convenience endpoint).
    
    Simple GET endpoint for quick checks.
    """
    try:
        validate_coordinates(lat, lng)
        
        result = await predictor.get_current_visibility(
            satellite_name=satellite_name,
            observer_lat=lat,
            observer_lng=lng,
            cloud_cover=cloud_cover,
            light_pollution=light_pollution
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Current visibility error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Current visibility check failed: {str(e)}"
        )


