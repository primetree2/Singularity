# astro-service/app/core/visibility.py
"""
High-level visibility prediction combining geometry, scoring, and external data.
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
import logging

from .geometry import GeometryCalculator
from .scoring import VisibilityScorer
from .tle import TLEManager

logger = logging.getLogger(__name__)


class VisibilityPredictor:
    """Main class for predicting satellite visibility."""

    def __init__(
        self,
        tle_manager: Optional[TLEManager] = None,
        geometry_calculator: Optional[GeometryCalculator] = None,
        scorer: Optional[VisibilityScorer] = None
    ):
        """
        Initialize predictor with optional custom components.

        Args:
            tle_manager: Custom TLE manager
            geometry_calculator: Custom geometry calculator
            scorer: Custom visibility scorer
        """
        self.tle_manager = tle_manager or TLEManager()
        self.geometry = geometry_calculator or GeometryCalculator()
        self.scorer = scorer or VisibilityScorer()

    async def predict_satellite_visibility(
        self,
        satellite_name: str,
        observer_lat: float,
        observer_lng: float,
        observation_time: datetime,
        observer_elevation: float = 0,
        cloud_cover: float = 0,
        light_pollution: float = 0.5,
        tle_source: str = 'celestrak_stations'
    ) -> Dict:
        """
        Predict visibility for a satellite at a specific time.

        Args:
            satellite_name: Name of satellite (e.g., "ISS")
            observer_lat: Observer latitude
            observer_lng: Observer longitude
            observation_time: Time to check visibility
            observer_elevation: Elevation in meters
            cloud_cover: Cloud coverage 0-100%
            light_pollution: Light pollution index 0-1
            tle_source: TLE data source

        Returns:
            Dict with visibility score and detailed breakdown
        """
        try:
            # Get satellite TLE
            satellite = await self.tle_manager.get_satellite_by_name(
                satellite_name, tle_source
            )

            if not satellite:
                return {
                    'error': f'Satellite not found: {satellite_name}',
                    'visible': False
                }

            # Ensure time is UTC
            if observation_time.tzinfo is None:
                observation_time = observation_time.replace(tzinfo=timezone.utc)
            else:
                # normalize to UTC
                observation_time = observation_time.astimezone(timezone.utc)

            # Calculate geometry
            sat_geometry = self.geometry.calculate_altitude_azimuth(
                satellite, observer_lat, observer_lng,
                observer_elevation, observation_time
            ) or {}

            # Get sun position
            sun_pos = self.geometry.calculate_sun_position(
                observer_lat, observer_lng, observation_time
            ) or {}

            # Get moon position
            moon_pos = self.geometry.calculate_moon_position(
                observer_lat, observer_lng, observation_time
            ) or {}

            # Safe get altitude
            altitude = sat_geometry.get('altitude', 0.0)

            # Calculate airmass (geometry should handle invalid altitudes)
            airmass = self.geometry.calculate_airmass(altitude)

            # Calculate visibility score
            visibility = self.scorer.calculate_score(
                elevation_degrees=altitude,
                sun_altitude=sun_pos.get('altitude', -999),
                cloud_cover_percent=cloud_cover,
                light_pollution_index=light_pollution,
                moon_altitude=moon_pos.get('altitude', -999),
                moon_illumination=moon_pos.get('illumination_percent', 0.0),
                airmass=airmass
            ) or {}

            overall_score = visibility.get('overall_score', 0.0)
            is_above = bool(sat_geometry.get('is_above_horizon', altitude > 0))

            return {
                'satellite': satellite_name,
                'observer': {
                    'latitude': observer_lat,
                    'longitude': observer_lng,
                    'elevation_m': observer_elevation
                },
                'observation_time': observation_time.isoformat(),
                'satellite_geometry': sat_geometry,
                'sun_position': sun_pos,
                'moon_position': moon_pos,
                'visibility': visibility,
                'visible': is_above and overall_score > 30,
                'recommended': overall_score >= 60
            }

        except Exception as e:
            logger.error(f"Error predicting visibility: {e}", exc_info=True)
            return {
                'error': str(e),
                'visible': False
            }

    async def find_next_visible_passes(
        self,
        satellite_name: str,
        observer_lat: float,
        observer_lng: float,
        days_ahead: int = 7,
        min_score: float = 50,
        cloud_cover: float = 0,
        light_pollution: float = 0.5
    ) -> List[Dict]:
        """
        Find all good visible passes in the next N days.

        Args:
            satellite_name: Name of satellite
            observer_lat: Observer latitude
            observer_lng: Observer longitude
            days_ahead: Days to search ahead
            min_score: Minimum visibility score to include
            cloud_cover: Expected cloud coverage
            light_pollution: Light pollution index

        Returns:
            List of pass predictions sorted by score (best first)
        """
        try:
            # Get satellite
            satellite = await self.tle_manager.get_satellite_by_name(satellite_name)
            if not satellite:
                return []

            # Get all passes
            start_time = datetime.now(timezone.utc)
            end_time = start_time + timedelta(days=days_ahead)

            passes = self.geometry.calculate_pass_times(
                satellite, observer_lat, observer_lng,
                start_time, days_ahead
            ) or []

            # Score each pass at peak time
            scored_passes = []
            for pass_info in passes:
                try:
                    peak_time = pass_info.get('peak')
                    if peak_time is None:
                        # fallback to mid-time between start and end if peak missing
                        start = pass_info.get('start')
                        end = pass_info.get('end')
                        if start and end:
                            peak_time = start + (end - start) / 2
                        else:
                            # skip malformed pass entry
                            continue

                    # normalize peak_time to UTC if naive
                    if peak_time.tzinfo is None:
                        peak_time = peak_time.replace(tzinfo=timezone.utc)
                    else:
                        peak_time = peak_time.astimezone(timezone.utc)

                    # Calculate geometry at peak
                    sat_geometry = self.geometry.calculate_altitude_azimuth(
                        satellite, observer_lat, observer_lng,
                        0, peak_time
                    ) or {}

                    altitude = sat_geometry.get('altitude', 0.0)
                    is_above = bool(sat_geometry.get('is_above_horizon', altitude > 0))

                    # get sun/moon positions at peak
                    sun_pos = self.geometry.calculate_sun_position(
                        observer_lat, observer_lng, peak_time
                    ) or {}
                    moon_pos = self.geometry.calculate_moon_position(
                        observer_lat, observer_lng, peak_time
                    ) or {}

                    airmass = self.geometry.calculate_airmass(altitude)

                    visibility = self.scorer.calculate_score(
                        elevation_degrees=altitude,
                        sun_altitude=sun_pos.get('altitude', -999),
                        cloud_cover_percent=cloud_cover,
                        light_pollution_index=light_pollution,
                        moon_altitude=moon_pos.get('altitude', -999),
                        moon_illumination=moon_pos.get('illumination_percent', 0.0),
                        airmass=airmass
                    ) or {}

                    overall_score = visibility.get('overall_score', 0.0)

                    # Only include passes meeting minimum score and above horizon
                    if is_above and overall_score >= min_score:
                        scored_passes.append({
                            'start': pass_info.get('start').isoformat() if pass_info.get('start') else None,
                            'end': pass_info.get('end').isoformat() if pass_info.get('end') else None,
                            'peak_time_iso': peak_time.isoformat(),
                            'max_elevation': altitude,
                            'satellite_geometry': sat_geometry,
                            'visibility': visibility,
                            'score': overall_score,
                            'visible': True
                        })
                except Exception:
                    logger.exception("Error scoring individual pass; skipping this pass.")

            # sort by score descending
            scored_passes.sort(key=lambda x: x.get('score', 0.0), reverse=True)
            return scored_passes

        except Exception as e:
            logger.error(f"Error finding next visible passes: {e}", exc_info=True)
            return []
