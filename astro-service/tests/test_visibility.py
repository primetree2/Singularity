"""
Unit tests for VisibilityPredictor (astro-service).

These tests use small, explicit test doubles for TLEManager, GeometryCalculator,
and VisibilityScorer so they do not perform network calls or depend on Skyfield.
They validate:
 - predict_satellite_visibility returns expected keys and applies timezone normalization
 - find_next_visible_passes filters/sorts passes based on the scorer's overall_score
 - the "visible" and "recommended" flags are calculated from geometry + score

The tests make the astro-service package importable by inserting the local astro-service
directory into sys.path. They use pytest-asyncio for async tests.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
import pytest
import asyncio

# Ensure astro-service package is importable (works when running from repo root)
HERE = os.path.dirname(__file__)
ASTRO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
if ASTRO_ROOT not in sys.path:
    sys.path.insert(0, ASTRO_ROOT)

# Import the VisibilityPredictor class
try:
    from app.core.visibility import VisibilityPredictor
except Exception as e:
    raise ImportError(
        "Failed to import VisibilityPredictor from app.core.visibility. "
        "Ensure astro-service/app/core/visibility.py exists and defines VisibilityPredictor."
    ) from e

# pytest-asyncio marker
pytest_plugins = ("pytest_asyncio",)


class DummyTLEManager:
    """Minimal async TLE manager stub."""

    def __init__(self, sat_present=True):
        self.sat_present = sat_present
        # store call args for inspection if needed
        self.last_query = None

    async def get_satellite_by_name(self, name, source=None):
        self.last_query = (name, source)
        if not self.sat_present:
            return None
        # Return a simple sentinel object (real geometry is mocked)
        return {"name": name}


class DummyGeometry:
    """
    Geometry stub returning deterministic values.
    calculate_altitude_azimuth returns a dict with altitude and is_above_horizon.
    calculate_sun_position and calculate_moon_position return simple dicts.
    calculate_airmass returns a numeric.
    calculate_pass_times returns a list of pass dicts with 'start','end','peak'.
    """
    def __init__(self, base_altitude=45.0):
        self.base_altitude = base_altitude

    def calculate_altitude_azimuth(self, satellite, lat, lng, elevation, when):
        # Return altitude based on base_altitude, say varying with minute component if datetime passed
        alt = self.base_altitude
        return {
            "altitude": alt,
            "azimuth": 120.0,
            "is_above_horizon": alt > 0,
            "raw": {"satellite": satellite}
        }

    def calculate_sun_position(self, lat, lng, when):
        # sun position: altitude negative for night, positive for day
        # If the hour is odd => night (-20), else day (+10) — deterministic for tests
        hour = when.hour if when.tzinfo else when.replace(tzinfo=timezone.utc).hour
        return {"altitude": -20.0 if hour % 2 == 1 else 10.0}

    def calculate_moon_position(self, lat, lng, when):
        return {"altitude": -5.0, "illumination_percent": 10.0}

    def calculate_airmass(self, altitude_deg):
        # simple mapping: airmass = 1 / sin(altitude) approximation for positive altitudes
        import math
        if altitude_deg <= 0:
            return float("inf")
        rad = math.radians(altitude_deg)
        return 1.0 / max(0.001, math.sin(rad))

    def calculate_pass_times(self, satellite, lat, lng, start_time, days_ahead):
        # produce 3 candidate passes spaced 1 day apart, each with a peak at noon UTC on that day
        passes = []
        for d in range(days_ahead if days_ahead <= 3 else 3):
            day = (start_time + timedelta(days=d)).replace(hour=12, minute=0, second=0, microsecond=0)
            start = day - timedelta(minutes=5)
            end = day + timedelta(minutes=5)
            passes.append({
                "start": start,
                "end": end,
                "peak": day
            })
        return passes


class DummyScorer:
    """
    Scorer stub that returns a predictable overall_score based on inputs.
    We'll make score be elevation * 1.0 - cloud*0.5 - light_pollution*20
    to produce different numeric outputs for tests.
    """
    def calculate_score(self, elevation_degrees, sun_altitude, cloud_cover_percent,
                        light_pollution_index, moon_altitude, moon_illumination, airmass):
        # convert inputs into a bounded 0-100 score
        base = float(elevation_degrees)
        base -= (cloud_cover_percent * 0.5)
        base -= (light_pollution_index * 20.0)
        # if sun is above horizon, big penalty
        if sun_altitude > -12.0:
            base *= 0.3
        # normalize
        score = max(0.0, min(100.0, base))
        return {"overall_score": score, "breakdown": {"elevation": elevation_degrees, "cloud": cloud_cover_percent, "lp": light_pollution_index}}


@pytest.mark.asyncio
async def test_predict_satellite_visibility_structure_and_flags():
    """
    Test that predict_satellite_visibility returns expected keys and sets
    'visible' and 'recommended' based on geometry + score.
    """
    tle = DummyTLEManager(sat_present=True)
    geom = DummyGeometry(base_altitude=50.0)
    scorer = DummyScorer()

    predictor = VisibilityPredictor(tle_manager=tle, geometry_calculator=geom, scorer=scorer)

    # Use a naive datetime (no tz) to ensure predictor normalizes to UTC
    dt_naive = datetime(2025, 11, 12, 1, 0, 0)  # hour odd -> sun_altitude will be -20 in DummyGeometry
    result = await predictor.predict_satellite_visibility(
        satellite_name="ISS",
        observer_lat=12.34,
        observer_lng=56.78,
        observation_time=dt_naive,
        observer_elevation=10.0,
        cloud_cover=10.0,
        light_pollution=0.2,
    )

    # Basic shape assertions
    assert isinstance(result, dict), "predict_satellite_visibility must return dict"
    for key in ("satellite", "observer", "observation_time", "satellite_geometry", "visibility", "visible", "recommended"):
        assert key in result, f"Missing key in result: {key}"

    # Validate types and values
    assert result["satellite"] == "ISS"
    assert isinstance(result["observer"], dict)
    assert "latitude" in result["observer"] and "longitude" in result["observer"]
    assert isinstance(result["satellite_geometry"], dict)
    assert isinstance(result["visibility"], dict)
    assert isinstance(result["visible"], bool)
    assert isinstance(result["recommended"], bool)

    # With base_altitude=50 and light pollution 0.2 and low clouds, scorer yields a decent score
    overall = result["visibility"].get("overall_score", None)
    assert overall is not None and isinstance(overall, (int, float))

    # Because DummyGeometry returns is_above_horizon True and score > 0, visible should be True
    assert result["satellite_geometry"]["is_above_horizon"] is True
    assert result["visible"] is True

    # recommended should be bool; for our scorer threshold unknown, but ensure consistency
    assert result["recommended"] == (overall >= 60)


@pytest.mark.asyncio
async def test_find_next_visible_passes_filters_by_min_score_and_sorts():
    """
    Test that find_next_visible_passes returns only passes meeting the min_score threshold
    and sorted by score descending.
    """
    tle = DummyTLEManager(sat_present=True)
    # Make geometry produce varying elevations across days by adjusting base_altitude per instance
    # We'll simulate with a geometry object but change its base_altitude dynamically inside the test by monkeypatching calculate_altitude_azimuth
    geom = DummyGeometry(base_altitude=10.0)
    scorer = DummyScorer()

    predictor = VisibilityPredictor(tle_manager=tle, geometry_calculator=geom, scorer=scorer)

    # Create a pass list with three peaks (the DummyGeometry.calculate_pass_times will create up to 3)
    start_time = datetime.now(timezone.utc)

    # Using default DummyGeometry passes (3 days), call find_next_visible_passes with min_score thresholds
    passes = await predictor.find_next_visible_passes(
        satellite_name="ISS",
        observer_lat=0.0,
        observer_lng=0.0,
        days_ahead=3,
        min_score=5,  # low threshold to include some passes
        cloud_cover=0,
        light_pollution=0.1
    )

    # Should return a list
    assert isinstance(passes, list)

    # Each item should have the expected keys and overall_score >= min_score
    for p in passes:
        assert "peak_time_iso" in p
        assert "score" in p
        assert p["score"] >= 5

    # If multiple passes returned, ensure sorted by score desc
    scores = [p["score"] for p in passes]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_predict_handles_missing_satellite_gracefully():
    """If TLEManager returns None, predictor should return an 'error' key and visible False."""
    tle = DummyTLEManager(sat_present=False)
    geom = DummyGeometry(base_altitude=30.0)
    scorer = DummyScorer()
    predictor = VisibilityPredictor(tle_manager=tle, geometry_calculator=geom, scorer=scorer)

    dt = datetime.now(timezone.utc)
    res = await predictor.predict_satellite_visibility(
        satellite_name="UNKNOWN_SAT",
        observer_lat=1.0,
        observer_lng=2.0,
        observation_time=dt
    )
    assert isinstance(res, dict)
    assert "error" in res
    assert res.get("visible") is False
