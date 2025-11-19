import type { User, Event, Event as EventType, VisibilityScore } from '../types/api-types';

/**
 * Remove sensitive fields from a user-like object and return a sanitized `User`.
 *
 * @param user - input object that should contain user-like fields
 * @returns User - sanitized user object
 * @throws TypeError if required fields are missing or invalid
 */
export function sanitizeUser(user: any): User {
  if (!user || typeof user !== 'object') {
    throw new TypeError('sanitizeUser: expected an object');
  }

  const { id, email, displayName, score, createdAt } = user;

  if (typeof id !== 'string') throw new TypeError('sanitizeUser: id must be a string');
  if (typeof email !== 'string') throw new TypeError('sanitizeUser: email must be a string');
  if (typeof displayName !== 'string') throw new TypeError('sanitizeUser: displayName must be a string');
  if (typeof score !== 'number') throw new TypeError('sanitizeUser: score must be a number');
  if (typeof createdAt !== 'string') throw new TypeError('sanitizeUser: createdAt must be a string');

  // Return only the safe public fields (explicitly drop password and other secrets)
  return {
    id,
    email,
    displayName,
    score,
    createdAt
  };
}

/**
 * Normalize and format an incoming event-like object into the `Event` shape.
 * Ensures date strings are valid ISO strings and required fields exist.
 *
 * This performs lightweight validation and will throw if required fields are missing.
 *
 * @param event - raw event object (from DB, API, or external source)
 * @returns Event - normalized Event object
 * @throws TypeError if required fields are missing or invalid
 */
export function formatEvent(event: any): Event {
  if (!event || typeof event !== 'object') {
    throw new TypeError('formatEvent: expected an object');
  }

  const { id, title, description = '', start, end = null, type, location, visibilityEstimate = null } = event;

  if (typeof id !== 'string') throw new TypeError('formatEvent: id must be a string');
  if (typeof title !== 'string') throw new TypeError('formatEvent: title must be a string');
  if (typeof type !== 'string') throw new TypeError('formatEvent: type must be a string');

  // validate and normalize dates
  const startDate = new Date(start);
  if (Number.isNaN(startDate.getTime())) throw new TypeError('formatEvent: invalid start date');

  const endDate = end ? new Date(end) : null;
  if (end && Number.isNaN(endDate!.getTime())) throw new TypeError('formatEvent: invalid end date');

  // location validation
  if (!location || typeof location !== 'object') {
    throw new TypeError('formatEvent: location is required and must be an object');
  }
  const lat = Number(location.lat);
  const lon = Number(location.lon);
  const name = location.name ? String(location.name) : '';

  if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
    throw new TypeError('formatEvent: location.lat and location.lon must be valid numbers');
  }

  // visibilityEstimate normalization if present
  let vis: VisibilityScore | null = null;
  if (visibilityEstimate) {
    const score = Number(visibilityEstimate.score);
    const updatedAtRaw = visibilityEstimate.updatedAt;
    const updatedAtDate = new Date(updatedAtRaw);
    if (!Number.isFinite(score) || Number.isNaN(updatedAtDate.getTime())) {
      throw new TypeError('formatEvent: invalid visibilityEstimate');
    }
    const factors = visibilityEstimate.factors && typeof visibilityEstimate.factors === 'object'
      ? visibilityEstimate.factors
      : {};
    vis = {
      score,
      updatedAt: updatedAtDate.toISOString(),
      factors: {
        cloudCover: Number(factors.cloudCover ?? 0),
        aqi: Number(factors.aqi ?? 0),
        lightPollution: Number(factors.lightPollution ?? 0),
        elevation: Number(factors.elevation ?? 0),
        moonIllumination: Number(factors.moonIllumination ?? 0),
        horizon: Number(factors.horizon ?? 0)
      }
    };
  }

  const formatted: Event = {
    id,
    title,
    description,
    start: startDate.toISOString(),
    end: endDate ? endDate.toISOString() : ('' as any),
    type,
    location: {
      lat,
      lon,
      name
    },
    visibilityEstimate: vis ?? ({ score: 0, updatedAt: new Date().toISOString() } as any)
  };

  return formatted;
}

/**
 * Calculate distance in kilometers between two geographic coordinates using the Haversine formula.
 *
 * @param lat1 - latitude of first point in decimal degrees
 * @param lon1 - longitude of first point in decimal degrees
 * @param lat2 - latitude of second point in decimal degrees
 * @param lon2 - longitude of second point in decimal degrees
 * @returns number - distance in kilometers (floating point)
 * @throws TypeError if inputs are not valid numbers
 */
export function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const toNumber = (v: any) => {
    const n = Number(v);
    if (!Number.isFinite(n)) throw new TypeError('calculateDistance: coordinates must be finite numbers');
    return n;
  };

  const φ1 = (toNumber(lat1) * Math.PI) / 180;
  const φ2 = (toNumber(lat2) * Math.PI) / 180;
  const Δφ = ((toNumber(lat2) - toNumber(lat1)) * Math.PI) / 180;
  const Δλ = ((toNumber(lon2) - toNumber(lon1)) * Math.PI) / 180;

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  const earthRadiusKm = 6371; // average radius
  return earthRadiusKm * c;
}
