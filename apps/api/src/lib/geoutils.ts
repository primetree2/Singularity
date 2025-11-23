import { calculateDistance } from '../utils/haversine';

/**
 * Find the nearest locations to a user's coordinates.
 *
 * Adds a `distance` property (in km) to each returned location and sorts the array
 * in ascending order by distance.
 *
 * @template T - location object type that must include `lat` and `lon`
 * @param userLat - user's latitude
 * @param userLon - user's longitude
 * @param locations - array of locations with { lat, lon }
 * @returns array of locations augmented with `distance` (in km) sorted by distance
 */
export function findNearest<T extends { lat: number; lon: number }>(
  userLat: number,
  userLon: number,
  locations: T[]
): Array<T & { distance: number }> {
  const withDistance = locations.map((loc) => {
    const distance = calculateDistance(userLat, userLon, loc.lat, loc.lon);
    return { ...(loc as T), distance };
  });

  withDistance.sort((a, b) => a.distance - b.distance);
  return withDistance;
}

/**
 * Check if two coordinates are within a given radius (kilometers).
 *
 * Uses the Haversine distance calculation under the hood.
 *
 * @param lat1 - first latitude
 * @param lon1 - first longitude
 * @param lat2 - second latitude
 * @param lon2 - second longitude
 * @param radiusKm - radius in kilometers
 * @returns true if distance <= radiusKm, false otherwise
 */
export function isWithinRadius(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number,
  radiusKm: number
): boolean {
  const dist = calculateDistance(lat1, lon1, lat2, lon2);
  return dist <= radiusKm;
}
