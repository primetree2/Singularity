# ============================================
# astro-service/app/models/prediction.py
# ============================================
"""
Pydantic models for prediction requests and responses.
These models handle validation, serialization, and documentation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, ConfigDict
from enum import Enum


# ============================================
# Enums
# ============================================

class TwilightPhase(str, Enum):
    """Types of twilight phases."""
    DAY = "day"
    CIVIL_TWILIGHT = "civil_twilight"
    NAUTICAL_TWILIGHT = "nautical_twilight"
    ASTRONOMICAL_TWILIGHT = "astronomical_twilight"
    NIGHT = "night"


class VisibilityInterpretation(str, Enum):
    """Visibility score interpretations."""
    EXCELLENT = "Excellent - Perfect viewing conditions"
    VERY_GOOD = "Very Good - Great viewing opportunity"
    GOOD = "Good - Visible with favorable conditions"
    FAIR = "Fair - Possible but challenging"
    POOR = "Poor - Difficult to see"
    VERY_POOR = "Very Poor - Not recommended"


class TLESource(str, Enum):
    """Available TLE data sources."""
    CELESTRAK_STATIONS = "celestrak_stations"
    CELESTRAK_VISUAL = "celestrak_visual"
    CELESTRAK_STARLINK = "celestrak_starlink"
    CELESTRAK_ACTIVE = "celestrak_active"


# ============================================
# Base Models
# ============================================

class ObserverLocation(BaseModel):
    """Observer location and elevation."""
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Observer latitude in degrees"
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Observer longitude in degrees"
    )
    elevation_m: float = Field(
        0,
        ge=0,
        le=10000,
        description="Elevation above sea level in meters"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "elevation_m": 10
            }
        }
    )


class EnvironmentalConditions(BaseModel):
    """Environmental conditions affecting visibility."""
    cloud_cover_percent: float = Field(
        0,
        ge=0,
        le=100,
        description="Cloud coverage percentage"
    )
    light_pollution_index: float = Field(
        0.5,
        ge=0,
        le=1,
        description="Light pollution index (0=dark sky, 1=bright city)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cloud_cover_percent": 20,
                "light_pollution_index": 0.7
            }
        }
    )


# ============================================
# Position Models
# ============================================

class SatelliteGeometry(BaseModel):
    """Satellite position geometry."""
    altitude: float = Field(..., description="Altitude above horizon in degrees")
    azimuth: float = Field(..., description="Azimuth in degrees (0=North, 90=East)")
    distance: float = Field(..., description="Distance from observer in kilometers")
    elevation_degrees: float = Field(..., description="Elevation angle (alias for altitude)")
    is_above_horizon: bool = Field(..., description="Whether satellite is visible above horizon")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "altitude": 42.5,
                "azimuth": 135.2,
                "distance": 850.3,
                "elevation_degrees": 42.5,
                "is_above_horizon": True
            }
        }
    )


class SunPosition(BaseModel):
    """Sun position and twilight information."""
    altitude: float = Field(..., description="Sun altitude in degrees")
    azimuth: float = Field(..., description="Sun azimuth in degrees")
    twilight_phase: TwilightPhase = Field(..., description="Current twilight phase")
    is_dark: bool = Field(..., description="Whether it's astronomical twilight or darker")
    is_night: bool = Field(..., description="Whether it's nautical twilight or darker")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "altitude": -15.3,
                "azimuth": 280.5,
                "twilight_phase": "nautical_twilight",
                "is_dark": True,
                "is_night": True
            }
        }
    )


class MoonPosition(BaseModel):
    """Moon position and phase information."""
    altitude: float = Field(..., description="Moon altitude in degrees")
    azimuth: float = Field(..., description="Moon azimuth in degrees")
    distance_km: float = Field(..., description="Distance to moon in kilometers")
    illumination_percent: float = Field(..., description="Moon illumination percentage (0-100)")
    phase_angle: float = Field(..., description="Phase angle in degrees")
    is_above_horizon: bool = Field(..., description="Whether moon is visible")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "altitude": 25.8,
                "azimuth": 180.3,
                "distance_km": 384400,
                "illumination_percent": 45.2,
                "phase_angle": 90.5,
                "is_above_horizon": True
            }
        }
    )


# ============================================
# Visibility Score Models
# ============================================

class VisibilityComponents(BaseModel):
    """Individual components of visibility score."""
    elevation: float = Field(..., ge=0, le=100, description="Elevation score")
    sun_angle: float = Field(..., ge=0, le=100, description="Darkness score")
    cloud_cover: float = Field(..., ge=0, le=100, description="Cloud coverage score")
    light_pollution: float = Field(..., ge=0, le=100, description="Light pollution score")
    moon_interference: float = Field(..., ge=0, le=100, description="Moon interference score")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "elevation": 85.2,
                "sun_angle": 92.1,
                "cloud_cover": 80.0,
                "light_pollution": 30.0,
                "moon_interference": 95.3
            }
        }
    )


class VisibilityScore(BaseModel):
    """Complete visibility scoring information."""
    overall_score: float = Field(..., ge=0, le=100, description="Overall visibility score")
    components: VisibilityComponents = Field(..., description="Component scores")
    airmass_factor: float = Field(..., description="Atmospheric airmass factor")
    weights_used: Dict[str, float] = Field(..., description="Weights applied to components")
    interpretation: str = Field(..., description="Human-readable interpretation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "overall_score": 78.5,
                "components": {
                    "elevation": 85.2,
                    "sun_angle": 92.1,
                    "cloud_cover": 80.0,
                    "light_pollution": 30.0,
                    "moon_interference": 95.3
                },
                "airmass_factor": 0.95,
                "weights_used": {
                    "elevation": 0.30,
                    "sun_angle": 0.25,
                    "cloud_cover": 0.20,
                    "light_pollution": 0.15,
                    "moon_interference": 0.10
                },
                "interpretation": "Very Good - Great viewing opportunity"
            }
        }
    )


# ============================================
# Request Models
# ============================================

class PredictionRequest(BaseModel):
    """Request for single-time visibility prediction."""
    satellite_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Satellite name (e.g., 'ISS', 'HUBBLE')"
    )
    observer_lat: float = Field(..., ge=-90, le=90, description="Observer latitude")
    observer_lng: float = Field(..., ge=-180, le=180, description="Observer longitude")
    observer_elevation: float = Field(
        0,
        ge=0,
        le=10000,
        description="Observer elevation in meters"
    )
    observation_time: Optional[datetime] = Field(
        None,
        description="Time to check visibility (UTC). If null, uses current time"
    )
    cloud_cover: float = Field(
        0,
        ge=0,
        le=100,
        description="Cloud coverage percentage"
    )
    light_pollution: float = Field(
        0.5,
        ge=0,
        le=1,
        description="Light pollution index"
    )
    tle_source: TLESource = Field(
        TLESource.CELESTRAK_STATIONS,
        description="TLE data source"
    )
    
    @validator('satellite_name')
    def validate_satellite_name(cls, v):
        """Validate and normalize satellite name."""
        v = v.strip()
        if not v:
            raise ValueError("Satellite name cannot be empty")
        return v.upper()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "satellite_name": "ISS",
                "observer_lat": 40.7128,
                "observer_lng": -74.0060,
                "observer_elevation": 10,
                "observation_time": "2024-12-01T20:30:00Z",
                "cloud_cover": 20,
                "light_pollution": 0.7,
                "tle_source": "celestrak_stations"
            }
        }
    )


class PassesRequest(BaseModel):
    """Request for finding upcoming passes."""
    satellite_name: str = Field(..., min_length=1, max_length=100)
    observer_lat: float = Field(..., ge=-90, le=90)
    observer_lng: float = Field(..., ge=-180, le=180)
    observer_elevation: float = Field(0, ge=0, le=10000)
    days_ahead: int = Field(
        7,
        ge=1,
        le=14,
        description="Number of days to search ahead"
    )
    min_score: float = Field(
        50,
        ge=0,
        le=100,
        description="Minimum visibility score to include"
    )
    min_altitude: float = Field(
        10,
        ge=0,
        le=90,
        description="Minimum altitude above horizon (degrees)"
    )
    cloud_cover: float = Field(0, ge=0, le=100)
    light_pollution: float = Field(0.5, ge=0, le=1)
    tle_source: TLESource = Field(TLESource.CELESTRAK_STATIONS)
    
    @validator('satellite_name')
    def validate_satellite_name(cls, v):
        """Validate and normalize satellite name."""
        v = v.strip()
        if not v:
            raise ValueError("Satellite name cannot be empty")
        return v.upper()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "satellite_name": "ISS",
                "observer_lat": 40.7128,
                "observer_lng": -74.0060,
                "days_ahead": 7,
                "min_score": 60,
                "min_altitude": 10,
                "light_pollution": 0.7
            }
        }
    )


# ============================================
# Response Models
# ============================================

class PredictionResponse(BaseModel):
    """Response for visibility prediction."""
    satellite: str = Field(..., description="Satellite name")
    observer: ObserverLocation = Field(..., description="Observer location")
    observation_time: str = Field(..., description="Observation time (ISO 8601)")
    satellite_geometry: SatelliteGeometry = Field(..., description="Satellite position")
    sun_position: SunPosition = Field(..., description="Sun position and twilight")
    moon_position: MoonPosition = Field(..., description="Moon position and phase")
    visibility: VisibilityScore = Field(..., description="Visibility scoring")
    visible: bool = Field(..., description="Whether satellite is visible")
    recommended: bool = Field(..., description="Whether viewing is recommended")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "satellite": "ISS (ZARYA)",
                "observer": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "elevation_m": 10
                },
                "observation_time": "2024-12-01T20:30:00Z",
                "satellite_geometry": {
                    "altitude": 42.5,
                    "azimuth": 135.2,
                    "distance": 850.3,
                    "elevation_degrees": 42.5,
                    "is_above_horizon": True
                },
                "sun_position": {
                    "altitude": -15.3,
                    "azimuth": 280.5,
                    "twilight_phase": "nautical_twilight",
                    "is_dark": True,
                    "is_night": True
                },
                "moon_position": {
                    "altitude": -10.2,
                    "azimuth": 90.1,
                    "distance_km": 384400,
                    "illumination_percent": 45.2,
                    "phase_angle": 90.5,
                    "is_above_horizon": False
                },
                "visibility": {
                    "overall_score": 78.5,
                    "components": {
                        "elevation": 85.2,
                        "sun_angle": 92.1,
                        "cloud_cover": 80.0,
                        "light_pollution": 30.0,
                        "moon_interference": 100.0
                    },
                    "airmass_factor": 0.95,
                    "weights_used": {
                        "elevation": 0.30,
                        "sun_angle": 0.25,
                        "cloud_cover": 0.20,
                        "light_pollution": 0.15,
                        "moon_interference": 0.10
                    },
                    "interpretation": "Very Good - Great viewing opportunity"
                },
                "visible": True,
                "recommended": True
            }
        }
    )


class PassInfo(BaseModel):
    """Information about a single satellite pass."""
    rise: str = Field(..., description="Rise time (ISO 8601)")
    peak: str = Field(..., description="Peak time (ISO 8601)")
    set: str = Field(..., description="Set time (ISO 8601)")
    duration_seconds: float = Field(..., description="Pass duration in seconds")
    max_altitude: float = Field(..., description="Maximum altitude in degrees")
    azimuth: float = Field(..., description="Azimuth at peak in degrees")
    visibility_score: float = Field(..., description="Visibility score at peak")
    visibility_details: VisibilityScore = Field(..., description="Detailed visibility breakdown")
    sun_position: SunPosition = Field(..., description="Sun position at peak")
    moon_position: MoonPosition = Field(..., description="Moon position at peak")
    recommended: bool = Field(..., description="Whether this pass is highly recommended")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rise": "2024-12-01T20:15:00Z",
                "peak": "2024-12-01T20:20:00Z",
                "set": "2024-12-01T20:25:00Z",
                "duration_seconds": 600,
                "max_altitude": 45.8,
                "azimuth": 180.5,
                "visibility_score": 82.3,
                "recommended": True
            }
        }
    )


class PassesResponse(BaseModel):
    """Response for passes search."""
    satellite: str = Field(..., description="Satellite name")
    observer: Dict[str, float] = Field(..., description="Observer location")
    search_criteria: Dict[str, Any] = Field(..., description="Search parameters used")
    total_passes: int = Field(..., description="Total number of passes found")
    passes: List[PassInfo] = Field(..., description="List of passes (sorted by score)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "satellite": "ISS (ZARYA)",
                "observer": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "search_criteria": {
                    "days_ahead": 7,
                    "min_score": 60,
                    "min_altitude": 10
                },
                "total_passes": 5,
                "passes": [
                    {
                        "rise": "2024-12-01T20:15:00Z",
                        "peak": "2024-12-01T20:20:00Z",
                        "set": "2024-12-01T20:25:00Z",
                        "duration_seconds": 600,
                        "max_altitude": 45.8,
                        "visibility_score": 82.3,
                        "recommended": True
                    }
                ]
            }
        }
    )


# ============================================
# Error Response Models
# ============================================

class ErrorDetail(BaseModel):
    """Detailed error information."""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error summary")
    detail: Optional[str] = Field(None, description="Detailed error message")
    errors: Optional[List[ErrorDetail]] = Field(None, description="List of validation errors")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Validation Error",
                "detail": "Invalid request parameters",
                "errors": [
                    {
                        "field": "observer_lat",
                        "message": "Latitude must be between -90 and 90",
                        "type": "value_error"
                    }
                ]
            }
        }
    )


# ============================================
# Satellite Model
# ============================================

class SatelliteInfo(BaseModel):
    """Basic satellite information."""
    name: str = Field(..., description="Satellite name")
    norad_id: Optional[str] = Field(None, description="NORAD catalog number")
    line1: Optional[str] = Field(None, description="TLE line 1")
    line2: Optional[str] = Field(None, description="TLE line 2")
    tle_age_hours: Optional[float] = Field(None, description="Age of TLE data in hours")
    source: Optional[str] = Field(None, description="TLE data source")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "ISS (ZARYA)",
                "norad_id": "25544",
                "tle_age_hours": 3.5,
                "source": "celestrak_stations"
            }
        }
    )


class SatelliteListItem(BaseModel):
    """Satellite list item."""
    name: str = Field(..., description="Satellite name")
    line1_preview: str = Field(..., description="First 20 chars of TLE line 1")
    line2_preview: str = Field(..., description="First 20 chars of TLE line 2")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "ISS (ZARYA)",
                "line1_preview": "1 25544U 98067A   ...",
                "line2_preview": "2 25544  51.6400 ..."
            }
        }
    )


class SatelliteListResponse(BaseModel):
    """Response for satellite list."""
    source: str = Field(..., description="TLE source")
    total: int = Field(..., description="Total number of satellites")
    satellites: List[SatelliteListItem] = Field(..., description="List of satellites")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source": "celestrak_stations",
                "total": 15,
                "satellites": [
                    {
                        "name": "ISS (ZARYA)",
                        "line1_preview": "1 25544U 98067A   ...",
                        "line2_preview": "2 25544  51.6400 ..."
                    }
                ]
            }
        }
    )


# ============================================
# Health Check Model
# ============================================

class HealthStatus(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status (healthy/unhealthy)")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    services: Dict[str, bool] = Field(..., description="Status of dependent services")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2024-12-01T20:30:00Z",
                "version": "1.0.0",
                "services": {
                    "redis": True,
                    "tle_manager": True,
                    "geometry_calculator": True
                }
            }
        }
    )