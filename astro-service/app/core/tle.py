# astro-service/app/core/tle.py
"""
TLE (Two-Line Element) data management.
Fetches, parses, and caches satellite orbital data.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone, timedelta
import httpx
from skyfield.api import EarthSatellite, load
import logging

logger = logging.getLogger(__name__)


class TLEManager:
    """Manages TLE data for satellites."""

    # Common TLE sources
    TLE_SOURCES = {
        'celestrak_stations': 'https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle',
        'celestrak_visual': 'https://celestrak.org/NORAD/elements/gp.php?GROUP=visual&FORMAT=tle',
        'celestrak_starlink': 'https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle',
        'celestrak_active': 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle',
    }

    def __init__(self, cache_ttl_hours: int = 6):
        """
        Initialize TLE manager.

        Args:
            cache_ttl_hours: How long to cache TLE data before refreshing
        """
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        # cache key -> { satellite: EarthSatellite, timestamp: datetime, tle_lines: (line1, line2) }
        self.tle_cache: Dict[str, Dict] = {}
        self.ts = load.timescale()

    async def fetch_tle_from_celestrak(
        self,
        source: str = 'celestrak_stations'
    ) -> List[Tuple[str, str, str]]:
        """
        Fetch TLE data from Celestrak.

        Args:
            source: Source key from TLE_SOURCES

        Returns:
            List of (name, line1, line2) tuples
        """
        url = self.TLE_SOURCES.get(source)
        if not url:
            raise ValueError(f"Unknown TLE source: {source}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()

                # Normalize line endings and parse
                text = response.text.replace('\r\n', '\n').replace('\r', '\n')
                tle_data = self._parse_tle_text(text)
                logger.info(f"Fetched {len(tle_data)} TLEs from {source}")
                return tle_data

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch TLE from {url}: {e}", exc_info=True)
            raise

    def _parse_tle_text(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Parse TLE text format into list of (name, line1, line2).

        Handles feeds with blank lines and variable line endings.
        """
        lines = [ln.strip() for ln in text.split('\n') if ln.strip() != '']
        tle_data: List[Tuple[str, str, str]] = []

        i = 0
        # Typical pattern: name line, line1 (starts with '1 '), line2 (starts with '2 ')
        while i < len(lines):
            # Look ahead to find a valid triple
            if i + 2 < len(lines):
                name = lines[i]
                line1 = lines[i + 1]
                line2 = lines[i + 2]

                if line1.startswith('1 ') and line2.startswith('2 '):
                    tle_data.append((name, line1, line2))
                    i += 3
                    continue
            # If not a valid triple, shift by one and try again
            i += 1

        return tle_data

    def create_satellite(
        self,
        name: str,
        line1: str,
        line2: str
    ) -> EarthSatellite:
        """
        Create Skyfield EarthSatellite object from TLE.

        Args:
            name: Satellite name
            line1: TLE line 1
            line2: TLE line 2

        Returns:
            EarthSatellite object ready for calculations
        """
        return EarthSatellite(line1, line2, name, self.ts)

    async def get_satellite_by_name(
        self,
        name: str,
        source: str = 'celestrak_stations'
    ) -> Optional[EarthSatellite]:
        """
        Get satellite by name, fetching TLE if not cached.

        Args:
            name: Satellite name (case-insensitive, partial match)
            source: TLE source to use

        Returns:
            EarthSatellite object or None if not found
        """
        # Cache key uses the requested name + source to avoid collisions
        cache_key = f"{source}:{name.upper()}"
        cached = self.tle_cache.get(cache_key)
        if cached:
            # Age check
            ts_now = datetime.now(timezone.utc)
            if ts_now - cached.get('timestamp', ts_now) < self.cache_ttl:
                logger.debug(f"Using cached TLE for {name}")
                return cached.get('satellite')

        # Fetch fresh TLE data
        tle_data = await self.fetch_tle_from_celestrak(source)

        # Search for satellite (partial, case-insensitive)
        name_upper = name.upper()
        for sat_name, line1, line2 in tle_data:
            if name_upper in sat_name.upper():
                try:
                    satellite = self.create_satellite(sat_name, line1, line2)
                except Exception as e:
                    logger.warning(f"Failed to create EarthSatellite for {sat_name}: {e}", exc_info=True)
                    continue

                # Cache it with the requested key so future requests for this name hit cache
                self.tle_cache[cache_key] = {
                    'satellite': satellite,
                    'timestamp': datetime.now(timezone.utc),
                    'tle_lines': (line1, line2)
                }

                logger.info(f"Found satellite: {sat_name}")
                return satellite

        logger.warning(f"Satellite not found: {name}")
        return None

    async def get_iss(self) -> EarthSatellite:
        """Convenience method to get ISS satellite."""
        iss = await self.get_satellite_by_name('ISS', 'celestrak_stations')
        if not iss:
            raise ValueError("Could not find ISS TLE data")
        return iss

    def validate_tle(self, line1: str, line2: str) -> bool:
        """
        Validate TLE format and checksum.

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check line format
            if not (line1.startswith('1 ') and line2.startswith('2 ')):
                return False

            # Many TLEs are 69 characters long (without newline). Be forgiving:
            if len(line1) < 60 or len(line2) < 60:
                # Too short to be valid TLE
                return False

            # Validate checksums (best-effort)
            if not (self._verify_tle_checksum(line1) and self._verify_tle_checksum(line2)):
                return False

            # Try to create satellite (will raise if invalid)
            self.create_satellite("TEST", line1, line2)
            return True

        except Exception as e:
            logger.error(f"TLE validation failed: {e}", exc_info=True)
            return False

    def _verify_tle_checksum(self, line: str) -> bool:
        """Verify TLE line checksum.

        Per TLE spec: the last character is a single digit checksum. Non-digit => invalid.
        """
        if len(line) < 1:
            return False

        chk_char = line[-1]
        if not chk_char.isdigit():
            return False

        # Sum digits and count '-' as 1, ignore other chars
        checksum = 0
        for char in line[:-1]:
            if char.isdigit():
                checksum += int(char)
            elif char == '-':
                checksum += 1
            # spaces and letters contribute 0

        try:
            expected_checksum = int(chk_char)
        except ValueError:
            return False

        return (checksum % 10) == expected_checksum

    def get_tle_age(self, line1: str) -> timedelta:
        """
        Get age of TLE data from epoch in line 1.

        Returns:
            Time since TLE epoch. If parsing fails, returns a large timedelta.
        """
        try:
            # Ensure enough length to slice safely
            if len(line1) < 32:
                raise ValueError("TLE line1 too short to extract epoch")

            # Extract epoch from line 1 (columns 19-32 using 1-based TLE spec)
            epoch_str = line1[18:32].strip()
            # Parse epoch (format: YYDDD.DDDDDDDD or YYYY.DDD...)
            # Typical TLE uses YY as two-digit year and day-of-year fractional.
            year_part = epoch_str[:2]
            rest = epoch_str[2:]
            year = int(year_part)
            year = 2000 + year if year < 57 else 1900 + year
            day_of_year = float(rest)

            epoch = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_of_year - 1)
            return datetime.now(timezone.utc) - epoch

        except Exception as e:
            logger.warning(f"Could not parse TLE epoch from line: {e}", exc_info=True)
            # Return a very large age so callers treat it as stale/invalid
            return timedelta.max
