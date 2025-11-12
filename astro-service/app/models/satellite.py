# ============================================
# astro-service/app/models/satellite.py
# ============================================
"""
Pydantic models for satellite data and TLE information.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, ConfigDict
from enum import Enum


# ============================================
# Enums
# ============================================

class TLESource(str, Enum):
    """Available TLE data sources from Celestrak."""
    STATIONS = "celestrak_stations"
    VISUAL = "celestrak_visual"
    STARLINK = "celestrak_starlink"
    ACTIVE = "celestrak_active"


class SatelliteType(str, Enum):
    """Types of satellites."""
    SPACE_STATION = "space_station"
    COMMUNICATIONS = "communications"
    EARTH_OBSERVATION = "earth_observation"
    NAVIGATION = "navigation"
    SCIENTIFIC = "scientific"
    MILITARY = "military"
    WEATHER = "weather"
    DEBRIS = "debris"
    OTHER = "other"


class SatelliteStatus(str, Enum):
    """Operational status of satellites."""
    OPERATIONAL = "operational"
    NON_OPERATIONAL = "non_operational"
    DECAYED = "decayed"
    UNKNOWN = "unknown"


# ============================================
# TLE Models
# ============================================

class TLEData(BaseModel):
    """Two-Line Element set data."""
    line1: str = Field(
        ...,
        min_length=69,
        max_length=69,
        description="TLE line 1 (69 characters)"
    )
    line2: str = Field(
        ...,
        min_length=69,
        max_length=69,
        description="TLE line 2 (69 characters)"
    )
    
    @validator('line1')
    def validate_line1_format(cls, v):
        """Validate TLE line 1 format."""
        if not v.startswith('1 '):
            raise ValueError("Line 1 must start with '1 '")
        if len(v) != 69:
            raise ValueError("Line 1 must be exactly 69 characters")
        return v
    
    @validator('line2')
    def validate_line2_format(cls, v):
        """Validate TLE line 2 format."""
        if not v.startswith('2 '):
            raise ValueError("Line 2 must start with '2 '")
        if len(v) != 69:
            raise ValueError("Line 2 must be exactly 69 characters")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "line1": "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9005",
                "line2": "2 25544  51.6400 123.4567 0001234  12.3456  78.9012 15.50000000123456"
            }
        }
    )


class TLEInfo(BaseModel):
    """Complete TLE information with metadata."""
    satellite_name: str = Field(..., description="Satellite name")
    norad_id: str = Field(..., description="NORAD catalog number")
    tle: TLEData = Field(..., description="TLE data")
    epoch: datetime = Field(..., description="TLE epoch (time of data)")
    age_hours: float = Field(..., description="Age of TLE data in hours")
    source: TLESource = Field(..., description="Data source")
    last_updated: datetime = Field(..., description="When TLE was last fetched")
    is_valid: bool = Field(True, description="Whether TLE passes validation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "satellite_name": "ISS (ZARYA)",
                "norad_id": "25544",
                "tle": {
                    "line1": "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9005",
                    "line2": "2 25544  51.6400 123.4567 0001234  12.3456  78.9012 15.50000000123456"
                },
                "epoch": "2024-01-01T12:00:00Z",
                "age_hours": 3.5,
                "source": "celestrak_stations",
                "last_updated": "2024-12-01T20:30:00Z",
                "is_valid": True
            }
        }
    )


class TLEValidationResult(BaseModel):
    """Result of TLE validation."""
    valid: bool = Field(..., description="Whether TLE is valid")
    message: str = Field(..., description="Validation message")
    errors: Optional[List[str]] = Field(None, description="List of validation errors")
    age_days: Optional[float] = Field(None, description="Age of TLE in days")
    checksum_valid: bool = Field(..., description="Whether checksum is valid")
    format_valid: bool = Field(..., description="Whether format is valid")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "valid": True,
                "message": "TLE format and checksum are valid",
                "errors": None,
                "age_days": 0.15,
                "checksum_valid": True,
                "format_valid": True
            }
        }
    )


# ============================================
# Orbital Elements Models
# ============================================

class OrbitalElements(BaseModel):
    """Keplerian orbital elements extracted from TLE."""
    inclination: float = Field(..., description="Inclination in degrees")
    raan: float = Field(..., description="Right Ascension of Ascending Node (degrees)")
    eccentricity: float = Field(..., description="Eccentricity (dimensionless)")
    argument_of_perigee: float = Field(..., description="Argument of perigee (degrees)")
    mean_anomaly: float = Field(..., description="Mean anomaly (degrees)")
    mean_motion: float = Field(..., description="Mean motion (revolutions per day)")
    revolution_number: int = Field(..., description="Revolution number at epoch")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "inclination": 51.6400,
                "raan": 123.4567,
                "eccentricity": 0.0001234,
                "argument_of_perigee": 12.3456,
                "mean_anomaly": 78.9012,
                "mean_motion": 15.50000000,
                "revolution_number": 12345
            }
        }
    )


class OrbitInfo(BaseModel):
    """Derived orbital information."""
    apogee_km: float = Field(..., description="Apogee altitude in km")
    perigee_km: float = Field(..., description="Perigee altitude in km")
    period_minutes: float = Field(..., description="Orbital period in minutes")
    semi_major_axis_km: float = Field(..., description="Semi-major axis in km")
    altitude_avg_km: float = Field(..., description="Average altitude in km")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "apogee_km": 425.0,
                "perigee_km": 415.0,
                "period_minutes": 92.9,
                "semi_major_axis_km": 6791.0,
                "altitude_avg_km": 420.0
            }
        }
    )


# ============================================
# Satellite Information Models
# ============================================

class SatelliteBasicInfo(BaseModel):
    """Basic satellite information."""
    name: str = Field(..., description="Satellite name")
    norad_id: Optional[str] = Field(None, description="NORAD catalog number")
    international_designator: Optional[str] = Field(None, description="International designator (COSPAR ID)")
    satellite_type: Optional[SatelliteType] = Field(None, description="Type of satellite")
    status: Optional[SatelliteStatus] = Field(SatelliteStatus.UNKNOWN, description="Operational status")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "ISS (ZARYA)",
                "norad_id": "25544",
                "international_designator": "1998-067A",
                "satellite_type": "space_station",
                "status": "operational"
            }
        }
    )


class SatelliteDetailedInfo(BaseModel):
    """Detailed satellite information."""
    basic_info: SatelliteBasicInfo = Field(..., description="Basic satellite information")
    tle_info: TLEInfo = Field(..., description="Current TLE data")
    orbital_elements: Optional[OrbitalElements] = Field(None, description="Orbital elements")
    orbit_info: Optional[OrbitInfo] = Field(None, description="Derived orbital information")
    country: Optional[str] = Field(None, description="Country of origin")
    launch_date: Optional[datetime] = Field(None, description="Launch date")
    launch_site: Optional[str] = Field(None, description="Launch site")
    mass_kg: Optional[float] = Field(None, description="Mass in kilograms")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "basic_info": {
                    "name": "ISS (ZARYA)",
                    "norad_id": "25544",
                    "international_designator": "1998-067A",
                    "satellite_type": "space_station",
                    "status": "operational"
                },
                "tle_info": {
                    "satellite_name": "ISS (ZARYA)",
                    "norad_id": "25544",
                    "age_hours": 3.5,
                    "source": "celestrak_stations"
                },
                "country": "International",
                "launch_date": "1998-11-20T00:00:00Z",
                "launch_site": "Baikonur Cosmodrome"
            }
        }
    )


class SatelliteSummary(BaseModel):
    """Summary information for satellite lists."""
    name: str = Field(..., description="Satellite name")
    norad_id: Optional[str] = Field(None, description="NORAD catalog number")
    satellite_type: Optional[SatelliteType] = Field(None, description="Type")
    tle_age_hours: Optional[float] = Field(None, description="TLE age in hours")
    line1_preview: str = Field(..., description="First 30 chars of TLE line 1")
    line2_preview: str = Field(..., description="First 30 chars of TLE line 2")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "ISS (ZARYA)",
                "norad_id": "25544",
                "satellite_type": "space_station",
                "tle_age_hours": 3.5,
                "line1_preview": "1 25544U 98067A   24001.500...",
                "line2_preview": "2 25544  51.6400 123.4567..."
            }
        }
    )


# ============================================
# Request Models
# ============================================

class TLERequest(BaseModel):
    """Request for TLE data."""
    satellite_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Satellite name (case-insensitive, partial match)"
    )
    source: TLESource = Field(
        TLESource.STATIONS,
        description="TLE data source"
    )
    force_refresh: bool = Field(
        False,
        description="Force fetch fresh data (ignore cache)"
    )
    
    @validator('satellite_name')
    def normalize_satellite_name(cls, v):
        """Normalize satellite name."""
        return v.strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "satellite_name": "ISS",
                "source": "celestrak_stations",
                "force_refresh": False
            }
        }
    )


class SatelliteSearchRequest(BaseModel):
    """Request for searching satellites."""
    query: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Search query (name or NORAD ID)"
    )
    source: Optional[TLESource] = Field(
        None,
        description="Limit search to specific source"
    )
    satellite_type: Optional[SatelliteType] = Field(
        None,
        description="Filter by satellite type"
    )
    limit: int = Field(
        50,
        ge=1,
        le=500,
        description="Maximum results to return"
    )
    
    @validator('query')
    def normalize_query(cls, v):
        """Normalize search query."""
        return v.strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "ISS",
                "source": "celestrak_stations",
                "satellite_type": "space_station",
                "limit": 10
            }
        }
    )


class TLEValidationRequest(BaseModel):
    """Request for TLE validation."""
    line1: str = Field(..., description="TLE line 1")
    line2: str = Field(..., description="TLE line 2")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "line1": "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9005",
                "line2": "2 25544  51.6400 123.4567 0001234  12.3456  78.9012 15.50000000123456"
            }
        }
    )


# ============================================
# Response Models
# ============================================

class SatelliteListResponse(BaseModel):
    """Response for satellite list."""
    source: str = Field(..., description="Data source")
    total_available: int = Field(..., description="Total satellites available")
    returned: int = Field(..., description="Number of satellites returned")
    satellites: List[SatelliteSummary] = Field(..., description="List of satellites")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source": "celestrak_stations",
                "total_available": 15,
                "returned": 10,
                "satellites": [
                    {
                        "name": "ISS (ZARYA)",
                        "norad_id": "25544",
                        "satellite_type": "space_station",
                        "tle_age_hours": 3.5,
                        "line1_preview": "1 25544U 98067A   24001.500...",
                        "line2_preview": "2 25544  51.6400 123.4567..."
                    }
                ]
            }
        }
    )


class SatelliteSearchResponse(BaseModel):
    """Response for satellite search."""
    query: str = Field(..., description="Search query used")
    matches: int = Field(..., description="Number of matches found")
    satellites: List[SatelliteSummary] = Field(..., description="Matching satellites")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "ISS",
                "matches": 1,
                "satellites": [
                    {
                        "name": "ISS (ZARYA)",
                        "norad_id": "25544",
                        "tle_age_hours": 3.5
                    }
                ]
            }
        }
    )


class TLESourcesResponse(BaseModel):
    """Response for available TLE sources."""
    sources: List[str] = Field(..., description="List of available sources")
    default: str = Field(..., description="Default source")
    descriptions: Dict[str, str] = Field(..., description="Source descriptions")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sources": [
                    "celestrak_stations",
                    "celestrak_visual",
                    "celestrak_starlink",
                    "celestrak_active"
                ],
                "default": "celestrak_stations",
                "descriptions": {
                    "celestrak_stations": "Space stations (ISS, Tiangong, etc.)",
                    "celestrak_visual": "Brightest satellites visible to naked eye",
                    "celestrak_starlink": "Starlink constellation",
                    "celestrak_active": "All active satellites"
                }
            }
        }
    )


# ============================================
# Special Satellite Models (ISS, Starlink, etc.)
# ============================================

class ISSInfo(BaseModel):
    """Special model for ISS information."""
    name: str = Field(default="ISS (ZARYA)", description="ISS name")
    norad_id: str = Field(default="25544", description="NORAD ID")
    tle: TLEInfo = Field(..., description="Current TLE")
    crew_size: Optional[int] = Field(None, description="Current crew size")
    altitude_km: Optional[float] = Field(None, description="Current altitude")
    speed_kmh: Optional[float] = Field(None, description="Current speed")
    description: str = Field(
        default="International Space Station - A habitable artificial satellite in low Earth orbit",
        description="ISS description"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "ISS (ZARYA)",
                "norad_id": "25544",
                "crew_size": 7,
                "altitude_km": 420.0,
                "speed_kmh": 27600,
                "description": "International Space Station"
            }
        }
    )


class StarlinkInfo(BaseModel):
    """Information about Starlink satellites."""
    name: str = Field(..., description="Starlink satellite name")
    norad_id: str = Field(..., description="NORAD ID")
    tle: TLEInfo = Field(..., description="Current TLE")
    shell: Optional[str] = Field(None, description="Starlink shell number")
    generation: Optional[int] = Field(None, description="Starlink generation (1, 2, etc.)")
    launch_date: Optional[datetime] = Field(None, description="Launch date")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "STARLINK-1234",
                "norad_id": "45678",
                "shell": "Shell 1",
                "generation": 2,
                "launch_date": "2023-06-15T00:00:00Z"
            }
        }
    )


# ============================================
# Batch Operations
# ============================================

class BatchTLERequest(BaseModel):
    """Request for multiple TLEs at once."""
    satellite_names: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of satellite names"
    )
    source: TLESource = Field(TLESource.STATIONS, description="TLE source")
    
    @validator('satellite_names')
    def validate_satellite_names(cls, v):
        """Validate and normalize satellite names."""
        if len(v) > 50:
            raise ValueError("Maximum 50 satellites per batch request")
        return [name.strip() for name in v if name.strip()]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "satellite_names": ["ISS", "HUBBLE", "TIANGONG"],
                "source": "celestrak_stations"
            }
        }
    )


class BatchTLEResponse(BaseModel):
    """Response for batch TLE request."""
    requested: int = Field(..., description="Number of satellites requested")
    found: int = Field(..., description="Number of satellites found")
    not_found: List[str] = Field(..., description="Satellites not found")
    satellites: List[TLEInfo] = Field(..., description="TLE data for found satellites")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "requested": 3,
                "found": 2,
                "not_found": ["HUBBLE"],
                "satellites": [
                    {
                        "satellite_name": "ISS (ZARYA)",
                        "norad_id": "25544",
                        "age_hours": 3.5
                    }
                ]
            }
        }
    )


# ============================================
# Statistics Models
# ============================================

class TLEStatistics(BaseModel):
    """Statistics about TLE cache and data."""
    total_cached: int = Field(..., description="Total TLEs in cache")
    sources: Dict[str, int] = Field(..., description="Count per source")
    oldest_tle_hours: float = Field(..., description="Age of oldest TLE in hours")
    newest_tle_hours: float = Field(..., description="Age of newest TLE in hours")
    average_age_hours: float = Field(..., description="Average TLE age in hours")
    cache_hit_rate: Optional[float] = Field(None, description="Cache hit rate percentage")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_cached": 150,
                "sources": {
                    "celestrak_stations": 15,
                    "celestrak_visual": 100,
                    "celestrak_starlink": 35
                },
                "oldest_tle_hours": 5.8,
                "newest_tle_hours": 0.5,
                "average_age_hours": 2.3,
                "cache_hit_rate": 87.5
            }
        }
    )