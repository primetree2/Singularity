import type { User, Event } from '../src';
import { calculateDistance } from '../src';

describe('shared types and utils', () => {
  test('should have valid User type', () => {
    const u: User = {
      id: 'user-1',
      email: 'test@example.com',
      displayName: 'Tester',
      score: 42,
      createdAt: new Date().toISOString()
    };

    expect(u).toBeDefined();
    expect(typeof u.email).toBe('string');
    expect(typeof u.score).toBe('number');
  });

  test('should have valid Event type', () => {
    const e: Event = {
      id: 'evt-1',
      title: 'Test Event',
      description: 'An example event',
      start: new Date().toISOString(),
      end: new Date(Date.now() + 3600 * 1000).toISOString(),
      type: 'MOON_PHASE',
      location: {
        lat: 51.5074,
        lon: -0.1278,
        name: 'London'
      },
      visibilityEstimate: {
        score: 75,
        updatedAt: new Date().toISOString()
      }
    };

    expect(e).toBeDefined();
    expect(e.location).toHaveProperty('lat');
    expect(typeof e.title).toBe('string');
  });

  test('calculateDistance should work', () => {
    // London -> Paris approx ~343 km
    const london = { lat: 51.5074, lon: -0.1278 };
    const paris = { lat: 48.8566, lon: 2.3522 };

    const d = calculateDistance(london.lat, london.lon, paris.lat, paris.lon);
    expect(typeof d).toBe('number');
    expect(d).toBeGreaterThan(300);
    expect(d).toBeLessThan(400);
  });
});
