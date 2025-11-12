"""
Unit tests for the visibility scoring logic.

These tests assume the astro-service package layout:
astro-service/
  app/
    core/
      scoring.py   <- defines VisibilityScorer with calculate_score(...)
  tests/
    test_scoring.py  <- this file

The test adds the parent astro-service directory to sys.path so that `app` can be imported.
The tests are defensive: they check that calculate_score returns a dict with an
'overall_score' between 0 and 100, and verify expected monotonic behaviour for a few inputs.
"""

import os
import sys
import math
import pytest

# Make the astro-service package importable (works when running from repo root)
HERE = os.path.dirname(__file__)
ASTRO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
if ASTRO_ROOT not in sys.path:
    sys.path.insert(0, ASTRO_ROOT)

# Now import the scorer
try:
    from app.core.scoring import VisibilityScorer
except Exception as e:
    raise ImportError(
        "Failed to import VisibilityScorer from app.core.scoring. "
        "Ensure astro-service/app/core/scoring.py exists and defines VisibilityScorer."
    ) from e


@pytest.fixture
def scorer():
    """Return a fresh VisibilityScorer instance for tests."""
    return VisibilityScorer()


def _score(scorer, elevation, sun_alt=-20.0, cloud=0.0, lp=0.2, moon_alt=-10.0, moon_illum=0.0, airmass=1.0):
    """
    Helper to call calculate_score with a typical argument set.
    Keeps parameter names aligned with the rest of the service code.
    """
    return scorer.calculate_score(
        elevation_degrees=elevation,
        sun_altitude=sun_alt,
        cloud_cover_percent=cloud,
        light_pollution_index=lp,
        moon_altitude=moon_alt,
        moon_illumination=moon_illum,
        airmass=airmass
    )


def test_calculate_score_returns_expected_structure(scorer):
    """Score result must be a dict containing 'overall_score' (0..100) and breakdown keys."""
    result = _score(scorer, elevation=30.0)
    assert isinstance(result, dict), "calculate_score must return a dict"
    assert 'overall_score' in result, "Result must include 'overall_score'"
    overall = result['overall_score']
    assert isinstance(overall, (int, float)), "'overall_score' must be numeric"
    assert 0.0 <= overall <= 100.0, "overall_score must be between 0 and 100"

    # Optionally check for breakdown keys if scorer returns them
    # (non-fatal — only assert existence if present)
    if 'breakdown' in result:
        assert isinstance(result['breakdown'], dict)


def test_score_increases_with_elevation(scorer):
    """
    Higher elevation (object higher above horizon) should yield a larger score,
    all else equal.
    """
    low = _score(scorer, elevation=5.0)       # near horizon, low
    high = _score(scorer, elevation=60.0)     # high pass, good
    assert low['overall_score'] <= high['overall_score'], (
        "Score should not decrease when elevation increases (all else equal)"
    )
    # Additionally ensure some meaningful difference (not identical)
    assert not math.isclose(low['overall_score'], high['overall_score'], rel_tol=1e-6), (
        "Expected a different score for different elevations"
    )


def test_night_vs_day_scores(scorer):
    """Pass at night (sun well below horizon) should score higher than in daylight."""
    night = _score(scorer, elevation=40.0, sun_alt=-30.0)
    day = _score(scorer, elevation=40.0, sun_alt=10.0)
    assert night['overall_score'] >= day['overall_score'], "Night score should be >= day score"


def test_cloud_and_light_pollution_reduce_score(scorer):
    """Increasing cloud cover or light pollution should reduce the score."""
    base = _score(scorer, elevation=45.0, cloud=0.0, lp=0.1)
    cloudy = _score(scorer, elevation=45.0, cloud=80.0, lp=0.1)
    polluted = _score(scorer, elevation=45.0, cloud=0.0, lp=0.8)

    assert base['overall_score'] >= cloudy['overall_score'], "Higher cloud cover should lower score"
    assert base['overall_score'] >= polluted['overall_score'], "Higher light pollution should lower score"


def test_airmass_effect(scorer):
    """Higher airmass (object lower in sky) should reduce score relative to low airmass."""
    low_airmass = _score(scorer, elevation=60.0, airmass=1.0)
    high_airmass = _score(scorer, elevation=60.0, airmass=3.0)
    assert low_airmass['overall_score'] >= high_airmass['overall_score'], "Higher airmass should lower the score"
