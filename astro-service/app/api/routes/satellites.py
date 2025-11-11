# ============================================
# astro-service/app/api/routes/satellites.py
# ============================================
"""
Satellite data endpoints for TLE management and satellite info.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
import logging

from app.api.deps import (
    get_tle_manager,
    verify_api_key,
    get_settings,
    Settings
)
from app.core.tle import TLEManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/satellites", tags=["satellites"])


# ============================================
# Response Models
# ============================================

class TLEInfo(BaseModel):
    """TLE information for a satellite."""
    name: str
    line1: str
    line2: str
    norad_id: Optional[str] = None
    age_hours: Optional[float] = None


class SatelliteListResponse(BaseModel):
    """Response for satellite list."""
    source: str
    total: int
    satellites: List[dict]


# ============================================
# Endpoints
# ============================================

@router.get("/tle/{satellite_name}")
async def get_satellite_tle(
    satellite_name: str,
    source: str = Query("celestrak_stations", description="TLE source"),
    tle_manager: TLEManager = Depends(get_tle_manager),
    authenticated: bool = Depends(verify_api_key)
) -> TLEInfo:
    """
    Get TLE (Two-Line Element) data for a satellite.
    
    Returns the latest TLE data from Celestrak.
    TLE data is cached for 6 hours to reduce API calls.
    """
    try:
        # Validate source
        if source not in tle_manager.TLE_SOURCES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid source. Valid sources: {list(tle_manager.TLE_SOURCES.keys())}"
            )
        
        # Get satellite
        satellite = await tle_manager.get_satellite_by_name(satellite_name, source)
        
        if not satellite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Satellite '{satellite_name}' not found in source '{source}'"
            )
        
        # Get cached TLE lines
        cache_key = f"{source}:{satellite_name.upper()}"
        cached = tle_manager.tle_cache.get(cache_key)
        
        if cached:
            line1, line2 = cached['tle_lines']
            age = tle_manager.get_tle_age(line1)
            
            return TLEInfo(
                name=satellite.name,
                line1=line1,
                line2=line2,
                age_hours=age.total_seconds() / 3600
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TLE data not available in cache"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TLE fetch error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch TLE: {str(e)}"
        )


@router.get("/list")
async def list_satellites(
    source: str = Query("celestrak_stations", description="TLE source"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number to return"),
    tle_manager: TLEManager = Depends(get_tle_manager),
    authenticated: bool = Depends(verify_api_key)
) -> SatelliteListResponse:
    """
    List available satellites from a TLE source.
    
    Returns list of satellite names available for tracking.
    """
    try:
        # Validate source
        if source not in tle_manager.TLE_SOURCES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid source. Valid sources: {list(tle_manager.TLE_SOURCES.keys())}"
            )
        
        # Fetch TLE data
        tle_data = await tle_manager.fetch_tle_from_celestrak(source)
        
        # Extract satellite names
        satellites = [
            {
                "name": name,
                "line1_preview": line1[:20] + "...",
                "line2_preview": line2[:20] + "..."
            }
            for name, line1, line2 in tle_data[:limit]
        ]
        
        return SatelliteListResponse(
            source=source,
            total=len(tle_data),
            satellites=satellites
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Satellite list error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list satellites: {str(e)}"
        )


@router.get("/sources")
async def list_tle_sources(
    tle_manager: TLEManager = Depends(get_tle_manager),
    authenticated: bool = Depends(verify_api_key)
):
    """
    List available TLE data sources.
    
    Returns all configured Celestrak sources.
    """
    return {
        "sources": list(tle_manager.TLE_SOURCES.keys()),
        "default": "celestrak_stations",
        "descriptions": {
            "celestrak_stations": "Space stations (ISS, Tiangong, etc.)",
            "celestrak_visual": "Brightest satellites (visible to naked eye)",
            "celestrak_starlink": "Starlink constellation",
            "celestrak_active": "All active satellites"
        }
    }


@router.post("/tle/validate")
async def validate_tle_data(
    line1: str = Query(..., description="TLE line 1"),
    line2: str = Query(..., description="TLE line 2"),
    tle_manager: TLEManager = Depends(get_tle_manager),
    authenticated: bool = Depends(verify_api_key)
):
    """
    Validate TLE format and checksum.
    
    Useful for checking user-provided TLE data.
    """
    try:
        is_valid = tle_manager.validate_tle(line1, line2)
        
        if is_valid:
            # Extract basic info
            age = tle_manager.get_tle_age(line1)
            
            return {
                "valid": True,
                "age_days": age.total_seconds() / 86400,
                "message": "TLE format and checksum are valid"
            }
        else:
            return {
                "valid": False,
                "message": "Invalid TLE format or checksum"
            }
            
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}"
        }


@router.get("/iss")
async def get_iss_info(
    tle_manager: TLEManager = Depends(get_tle_manager),
    authenticated: bool = Depends(verify_api_key)
):
    """
    Convenience endpoint to get ISS information.
    
    Returns current TLE data for the International Space Station.
    """
    try:
        iss = await tle_manager.get_iss()
        
        # Get TLE from cache
        cache_key = "celestrak_stations:ISS"
        cached = tle_manager.tle_cache.get(cache_key)
        
        if cached:
            line1, line2 = cached['tle_lines']
            age = tle_manager.get_tle_age(line1)
            
            return {
                "name": iss.name,
                "tle": {
                    "line1": line1,
                    "line2": line2,
                    "age_hours": age.total_seconds() / 3600,
                    "last_updated": cached['timestamp'].isoformat()
                },
                "info": {
                    "description": "International Space Station",
                    "type": "Space Station",
                    "country": "International",
                    "altitude_km": "~420"
                }
            }
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ISS TLE not available"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ISS info error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ISS info: {str(e)}"
        )