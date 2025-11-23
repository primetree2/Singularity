import type { VisibilityScore } from '@singularity/shared';

/**
 * Compute pseudo-random but deterministic visibility factors & overall score.
 *
 * TODO: Replace factor generators with real APIs:
 *  - Weather (cloud cover, humidity)
 *  - AQI (Air Quality Index)
 *  - Light pollution (satellite data)
 *  - Elevation (topographic API)
 *  - Moon phase / illumination
 */
export async function computeVisibility(opts: {
  lat: number;
  lon: number;
  time?: Date;
}): Promise<VisibilityScore> {
  try {
    const { lat, lon } = opts;
    const time = opts.time ?? new Date();

    // Deterministic seed based on lat, lon, and timestamp (hours resolution)
    const seed =
      Math.abs(
        Math.floor(lat * 1000) +
          Math.floor(lon * 1000) +
          Math.floor(time.getTime() / 3600000)
      ) % 100000;

    // Simple deterministic pseudo-random generator
    const rand = (n: number) => {
      const x = Math.sin(seed + n) * 10000;
      return x - Math.floor(x);
    };

    // Factor generation (deterministic ranges)
    const factors = {
      cloudCover: rand(1), // 0–1
      aqi: Math.floor(rand(2) * 500), // 0–500
      lightPollution: rand(3), // 0–1
      elevation: Math.floor(rand(4) * 3000), // 0–3000
      moonIllumination: rand(5), // 0–1
      horizon: rand(6) // 0–1
    };

    // Weights
    const weights = {
      cloudCover: 0.25,
      aqi: 0.15,
      lightPollution: 0.20,
      elevation: 0.10,
      moonIllumination: 0.15,
      horizon: 0.15
    };

    // Normalize each factor to a performance score 0–1 (1 is best)
    const normalized = {
      cloudCover: 1 - factors.cloudCover, // Less cloud is better
      aqi: 1 - factors.aqi / 500, // Lower AQI is better
      lightPollution: 1 - factors.lightPollution,
      elevation: factors.elevation / 3000, // Higher elevation is better
      moonIllumination: 1 - factors.moonIllumination,
      horizon: factors.horizon // Higher is better
    };

    // Weighted score 0–100
    const score =
      (normalized.cloudCover * weights.cloudCover +
        normalized.aqi * weights.aqi +
        normalized.lightPollution * weights.lightPollution +
        normalized.elevation * weights.elevation +
        normalized.moonIllumination * weights.moonIllumination +
        normalized.horizon * weights.horizon) *
      100;

    return {
      score: Math.round(score * 100) / 100,
      updatedAt: new Date().toISOString(),
      factors
    };
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('computeVisibility error:', err);
    return {
      score: 0,
      updatedAt: new Date().toISOString(),
      factors: {
        cloudCover: 1,
        aqi: 500,
        lightPollution: 1,
        elevation: 0,
        moonIllumination: 1,
        horizon: 0
      }
    };
  }
}
