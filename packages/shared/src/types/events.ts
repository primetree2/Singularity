/**
 * Event types supported by the Singularity system.
 */
export enum EventType {
  METEOR_SHOWER = "METEOR_SHOWER",
  LUNAR_ECLIPSE = "LUNAR_ECLIPSE",
  SOLAR_ECLIPSE = "SOLAR_ECLIPSE",
  PLANET_CONJUNCTION = "PLANET_CONJUNCTION",
  ISS_PASS = "ISS_PASS",
  SATELLITE_PASS = "SATELLITE_PASS",
  COMET = "COMET",
  MOON_PHASE = "MOON_PHASE"
}

/**
 * Geographic location for an event or darksite.
 *
 * Example:
 * const loc: EventLocation = { lat: 28.7041, lon: 77.1025, name: "New Delhi" };
 */
export interface EventLocation {
  /** Latitude in decimal degrees */
  lat: number;
  /** Longitude in decimal degrees */
  lon: number;
  /** Optional human-readable name for the location */
  name?: string;
}

/**
 * Filters used when querying events.
 *
 * Example:
 * const filters: EventFilters = {
 *   type: EventType.METEOR_SHOWER,
 *   startDate: "2025-08-12T00:00:00Z",
 *   endDate: "2025-08-13T00:00:00Z",
 *   lat: 28.7041,
 *   lon: 77.1025,
 *   radius: 200
 * };
 */
export interface EventFilters {
  type?: EventType;
  startDate?: string;
  endDate?: string;
  lat?: number;
  lon?: number;
  /** Radius in kilometers for proximity search */
  radius?: number;
}
