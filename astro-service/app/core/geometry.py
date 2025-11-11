# ============================================
# astro-service/app/core/geometry.py
# ============================================
"""
Astronomical geometry calculations.
Handles altitude, azimuth, and coordinate transformations.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple, Optional, List
import math
from skyfield.api import load, wgs84, Topos
from skyfield.sgp4lib import EarthSatellite
import pytz


class GeometryCalculator:
    """Handles geometric calculations for celestial objects."""
    
    def __init__(self):
        """Initialize the geometry calculator with ephemeris data."""
        self.ts = load.timescale()
        # Load planetary ephemeris (cached automatically by Skyfield)
        self.planets = load('de421.bsp')
        self.earth = self.planets['earth']
        self.sun = self.planets['sun']
        self.moon = self.planets['moon']
    
    def calculate_altitude_azimuth(
        self,
        satellite: EarthSatellite,
        observer_lat: float,
        observer_lng: float,
        observer_elevation: float,
        time: datetime
    ) -> Dict[str, float]:
        """
        Calculate altitude and azimuth of a satellite from observer location.
        
        Args:
            satellite: Skyfield EarthSatellite object
            observer_lat: Observer latitude in degrees (-90 to 90)
            observer_lng: Observer longitude in degrees (-180 to 180)
            observer_elevation: Observer elevation in meters above sea level
            time: Observation time (datetime object)
        
        Returns:
            Dict with 'altitude', 'azimuth', 'distance', 'elevation_degrees'
        """
        # Create observer location
        observer = wgs84.latlon(observer_lat, observer_lng, elevation_m=observer_elevation)
        
        # Convert datetime to Skyfield time
        if time.tzinfo is None:
            time = time.replace(tzinfo=timezone.utc)
        t = self.ts.from_datetime(time)
        
        # Calculate topocentric position (relative to observer)
        difference = satellite - observer
        topocentric = difference.at(t)
        
        # Get altitude and azimuth
        alt, az, distance = topocentric.altaz()
        
        return {
            'altitude': alt.degrees,  # Degrees above horizon
            'azimuth': az.degrees,    # Degrees clockwise from North
            'distance': distance.km,  # Distance in kilometers
            'elevation_degrees': alt.degrees,  # Alias for altitude
            'is_above_horizon': alt.degrees > 0
        }
    
    def calculate_sun_position(
        self,
        observer_lat: float,
        observer_lng: float,
        time: datetime
    ) -> Dict[str, float]:
        """
        Calculate sun position for determining twilight/darkness.
        
        Args:
            observer_lat: Observer latitude
            observer_lng: Observer longitude
            time: Observation time
        
        Returns:
            Dict with sun altitude, azimuth, and twilight status
        """
        observer = wgs84.latlon(observer_lat, observer_lng)
        
        if time.tzinfo is None:
            time = time.replace(tzinfo=timezone.utc)
        t = self.ts.from_datetime(time)
        
        # Calculate sun position
        astrometric = observer.at(t).observe(self.sun)
        alt, az, distance = astrometric.apparent().altaz()
        
        sun_altitude = alt.degrees
        
        # Determine twilight phase
        twilight_phase = self._get_twilight_phase(sun_altitude)
        
        return {
            'altitude': sun_altitude,
            'azimuth': az.degrees,
            'twilight_phase': twilight_phase,
            'is_dark': sun_altitude < -12,  # Astronomical twilight
            'is_night': sun_altitude < -6,  # Nautical twilight
        }
    
    def calculate_moon_position(
        self,
        observer_lat: float,
        observer_lng: float,
        time: datetime
    ) -> Dict[str, float]:
        """
        Calculate moon position and phase.
        
        Returns:
            Dict with moon altitude, azimuth, phase, and illumination
        """
        observer = wgs84.latlon(observer_lat, observer_lng)
        
        if time.tzinfo is None:
            time = time.replace(tzinfo=timezone.utc)
        t = self.ts.from_datetime(time)
        
        # Calculate moon position
        astrometric = observer.at(t).observe(self.moon)
        alt, az, distance = astrometric.apparent().altaz()
        
        # Calculate moon phase (illumination percentage)
        # This is a simplified calculation
        sun_pos = self.earth.at(t).observe(self.sun)
        moon_pos = self.earth.at(t).observe(self.moon)
        
        # Phase angle
        phase_angle = sun_pos.separation_from(moon_pos).degrees
        illumination = (1 + math.cos(math.radians(phase_angle))) / 2 * 100
        
        return {
            'altitude': alt.degrees,
            'azimuth': az.degrees,
            'distance_km': distance.km,
            'illumination_percent': illumination,
            'phase_angle': phase_angle,
            'is_above_horizon': alt.degrees > 0
        }
    
    def calculate_airmass(self, altitude_degrees: float) -> float:
        """
        Calculate atmospheric airmass for extinction calculations.
        
        Uses simple plane-parallel approximation for altitudes > 10°
        More accurate Kasten-Young formula for lower altitudes.
        
        Args:
            altitude_degrees: Altitude above horizon in degrees
        
        Returns:
            Airmass value (1.0 at zenith, increases toward horizon)
        """
        if altitude_degrees <= 0:
            return float('inf')  # Below horizon
        
        # Convert to zenith angle
        zenith_angle = 90 - altitude_degrees
        zenith_rad = math.radians(zenith_angle)
        
        if altitude_degrees > 10:
            # Simple secant formula for high altitudes
            return 1.0 / math.cos(zenith_rad)
        else:
            # Kasten-Young formula for low altitudes (more accurate)
            return 1.0 / (math.cos(zenith_rad) + 0.50572 * (96.07995 - zenith_angle) ** -1.6364)
    
    def calculate_pass_times(
        self,
        satellite: EarthSatellite,
        observer_lat: float,
        observer_lng: float,
        start_time: datetime,
        days_ahead: int = 7,
        min_altitude: float = 10.0
    ) -> List[Dict]:
        """
        Calculate all visible passes for a satellite over the next N days.
        
        Args:
            satellite: EarthSatellite object
            observer_lat: Observer latitude
            observer_lng: Observer longitude
            start_time: Start searching from this time
            days_ahead: Number of days to search ahead
            min_altitude: Minimum altitude for visibility (degrees)
        
        Returns:
            List of pass dictionaries with rise, peak, and set times
        """
        observer = wgs84.latlon(observer_lat, observer_lng)
        
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        
        t0 = self.ts.from_datetime(start_time)
        t1 = self.ts.from_datetime(start_time + timedelta(days=days_ahead))
        
        # Find events (rise, culminate, set)
        t, events = satellite.find_events(observer, t0, t1, altitude_degrees=min_altitude)
        
        # Group events into passes
        passes = []
        current_pass = {}
        
        for ti, event in zip(t, events):
            if event == 0:  # Rise
                current_pass = {'rise': ti.utc_datetime()}
            elif event == 1:  # Culmination (peak)
                if 'rise' in current_pass:
                    current_pass['peak'] = ti.utc_datetime()
                    # Calculate peak altitude
                    result = self.calculate_altitude_azimuth(
                        satellite, observer_lat, observer_lng, 0, ti.utc_datetime()
                    )
                    current_pass['max_altitude'] = result['altitude']
                    current_pass['azimuth'] = result['azimuth']
            elif event == 2:  # Set
                if 'rise' in current_pass and 'peak' in current_pass:
                    current_pass['set'] = ti.utc_datetime()
                    current_pass['duration_seconds'] = (
                        current_pass['set'] - current_pass['rise']
                    ).total_seconds()
                    passes.append(current_pass)
                    current_pass = {}
        
        return passes
    
    def _get_twilight_phase(self, sun_altitude: float) -> str:
        """Determine twilight phase based on sun altitude."""
        if sun_altitude > -0.833:  # Sun is up (accounting for refraction)
            return 'day'
        elif sun_altitude > -6:
            return 'civil_twilight'
        elif sun_altitude > -12:
            return 'nautical_twilight'
        elif sun_altitude > -18:
            return 'astronomical_twilight'
        else:
            return 'night'
