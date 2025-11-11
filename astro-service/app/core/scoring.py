# ============================================
# astro-service/app/core/scoring.py
# ============================================
"""
Visibility scoring algorithm.
Combines multiple factors to produce a 0-100 visibility score.
"""

from typing import Dict, Optional
import math


class VisibilityScorer:
    """Calculate visibility scores based on multiple factors."""
    
    # Default weights for scoring factors
    DEFAULT_WEIGHTS = {
        'elevation': 0.30,         # How high above horizon
        'sun_angle': 0.25,         # Darkness (sun below horizon)
        'cloud_cover': 0.20,       # Cloud coverage
        'light_pollution': 0.15,   # Light pollution level
        'moon_interference': 0.10  # Moon brightness/position
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize scorer with custom weights.
        
        Args:
            weights: Optional dict to override default weights
        """
        self.weights = self.DEFAULT_WEIGHTS.copy()
        if weights:
            self.weights.update(weights)
        
        # Normalize weights to sum to 1.0
        total = sum(self.weights.values())
        self.weights = {k: v/total for k, v in self.weights.items()}
    
    def calculate_score(
        self,
        elevation_degrees: float,
        sun_altitude: float,
        cloud_cover_percent: float,
        light_pollution_index: float,
        moon_altitude: float = 0,
        moon_illumination: float = 0,
        airmass: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate overall visibility score.
        
        Args:
            elevation_degrees: Satellite altitude above horizon (0-90)
            sun_altitude: Sun altitude (-90 to 90, negative is below horizon)
            cloud_cover_percent: Cloud coverage (0-100)
            light_pollution_index: Light pollution (0-1, where 0 is dark)
            moon_altitude: Moon altitude above horizon
            moon_illumination: Moon illumination percentage (0-100)
            airmass: Atmospheric airmass (1.0 at zenith)
        
        Returns:
            Dict with overall score and component scores
        """
        # Calculate component scores
        elevation_score = self._score_elevation(elevation_degrees)
        sun_score = self._score_sun_angle(sun_altitude)
        cloud_score = self._score_cloud_cover(cloud_cover_percent)
        lp_score = self._score_light_pollution(light_pollution_index)
        moon_score = self._score_moon_interference(moon_altitude, moon_illumination)
        
        # Apply airmass penalty (atmospheric extinction)
        airmass_factor = self._calculate_airmass_factor(airmass)
        
        # Calculate weighted score
        components = {
            'elevation': elevation_score,
            'sun_angle': sun_score,
            'cloud_cover': cloud_score,
            'light_pollution': lp_score,
            'moon_interference': moon_score
        }
        
        # Weighted sum
        raw_score = sum(
            components[key] * self.weights[key]
            for key in components.keys()
        )
        
        # Apply airmass penalty
        final_score = raw_score * airmass_factor
        
        # Clamp to 0-100
        final_score = max(0, min(100, final_score))
        
        return {
            'overall_score': round(final_score, 2),
            'components': {k: round(v, 2) for k, v in components.items()},
            'airmass_factor': round(airmass_factor, 3),
            'weights_used': self.weights,
            'interpretation': self._interpret_score(final_score)
        }
    
    def _score_elevation(self, elevation: float) -> float:
        """
        Score based on elevation above horizon.
        
        0° = 0 score, 90° = 100 score
        Uses sigmoid curve for realistic falloff near horizon
        """
        if elevation <= 0:
            return 0
        
        # Sigmoid curve: better visibility at higher elevations
        # Peak visibility at 45-90 degrees
        normalized = elevation / 90.0
        return 100 * (1 - math.exp(-3 * normalized))
    
    def _score_sun_angle(self, sun_altitude: float) -> float:
        """
        Score based on sun position (darkness).
        
        sun > 0° (daylight) = 0 score
        sun < -18° (astronomical night) = 100 score
        """
        if sun_altitude > -0.833:  # Sun is up (with refraction)
            return 0
        elif sun_altitude < -18:  # Astronomical night
            return 100
        else:
            # Linear interpolation between twilight phases
            # -0.833 to -18 degrees maps to 0-100
            return ((sun_altitude + 0.833) / -17.167) * 100
    
    def _score_cloud_cover(self, cloud_cover: float) -> float:
        """
        Score based on cloud coverage.
        
        0% clouds = 100 score
        100% clouds = 0 score
        """
        return 100 - cloud_cover
    
    def _score_light_pollution(self, lp_index: float) -> float:
        """
        Score based on light pollution.
        
        Args:
            lp_index: 0 (dark) to 1 (bright city)
        
        Returns:
            0-100 score (0 = terrible, 100 = perfect dark sky)
        """
        # Invert: less light pollution = higher score
        return (1 - lp_index) * 100
    
    def _score_moon_interference(
        self,
        moon_altitude: float,
        moon_illumination: float
    ) -> float:
        """
        Score based on moon interference.
        
        Moon below horizon = 100 score
        Full moon at zenith = lowest score
        """
        if moon_altitude <= 0:
            return 100  # Moon is down, no interference
        
        # Combine altitude and brightness
        # Higher moon + brighter moon = more interference
        altitude_factor = moon_altitude / 90.0
        illumination_factor = moon_illumination / 100.0
        
        interference = altitude_factor * illumination_factor
        
        return 100 * (1 - interference)
    
    def _calculate_airmass_factor(self, airmass: float) -> float:
        """
        Calculate visibility reduction due to atmospheric extinction.
        
        Airmass of 1.0 (zenith) = 1.0 factor (no penalty)
        Higher airmass = lower factor
        """
        if airmass >= 10:  # Near horizon
            return 0.1
        
        # Exponential decay
        return math.exp(-0.15 * (airmass - 1))
    
    def _interpret_score(self, score: float) -> str:
        """Provide human-readable interpretation of score."""
        if score >= 85:
            return "Excellent - Perfect viewing conditions"
        elif score >= 70:
            return "Very Good - Great viewing opportunity"
        elif score >= 55:
            return "Good - Visible with favorable conditions"
        elif score >= 40:
            return "Fair - Possible but challenging"
        elif score >= 25:
            return "Poor - Difficult to see"
        else:
            return "Very Poor - Not recommended"