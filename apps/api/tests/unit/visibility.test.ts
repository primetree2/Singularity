import { computeVisibility } from '../../src/services/visibility.service';

describe('visibility.service', () => {
  const sample = { lat: 16.3067, lon: 80.4365, time: new Date('2025-11-23T00:00:00.000Z') };

  test('should return score between 0 and 100', async () => {
    const result = await computeVisibility({ lat: sample.lat, lon: sample.lon, time: sample.time });
    expect(result).toBeDefined();
    expect(typeof result.score).toBe('number');
    expect(result.score).toBeGreaterThanOrEqual(0);
    expect(result.score).toBeLessThanOrEqual(100);
  });

  test('should include all required factors', async () => {
    const result = await computeVisibility({ lat: sample.lat, lon: sample.lon, time: sample.time });
    expect(result).toHaveProperty('factors');
    const f = result.factors as Record<string, unknown>;
    expect(f).toHaveProperty('cloudCover');
    expect(f).toHaveProperty('aqi');
    expect(f).toHaveProperty('lightPollution');
    expect(f).toHaveProperty('elevation');
    expect(f).toHaveProperty('moonIllumination');
    expect(f).toHaveProperty('horizon');
  });

  test('should be deterministic for same inputs', async () => {
    const a = await computeVisibility({ lat: sample.lat, lon: sample.lon, time: sample.time });
    const b = await computeVisibility({ lat: sample.lat, lon: sample.lon, time: sample.time });
    expect(a.score).toEqual(b.score);
    expect(a.factors).toEqual(b.factors);
  });
});
