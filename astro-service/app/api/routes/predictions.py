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


