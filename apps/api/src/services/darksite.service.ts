import { PrismaClient } from '@prisma/client';
import type { DarkSite as SharedDarkSite } from '@singularity/shared';
import { findNearest } from '../lib/geoutils';

const prisma = new PrismaClient();

export async function getNearestDarkSites(
  lat: number,
  lon: number,
  limit: number = 10
): Promise<SharedDarkSite[]> {
  try {
    const rows = await prisma.darkSite.findMany();

    // Flatten lat/lon so findNearest can use them
    const locations = rows.map((r) => ({
      id: r.id,
      name: r.name,
      lat: r.lat,          // <-- flattened
      lon: r.lon,          // <-- flattened
      lightPollution: r.lightPollution,
      description: r.description
    }));

    const sorted = findNearest(lat, lon, locations);

    return sorted.slice(0, limit).map((s) => ({
      id: s.id,
      name: s.name,
      location: { lat: s.lat, lon: s.lon },
      lightPollution: s.lightPollution,
      description: s.description,
      distance: s.distance
    }));
  } catch (err) {
    console.error('getNearestDarkSites error:', err);
    return [];
  }
}

export async function getDarkSiteById(id: string): Promise<SharedDarkSite | null> {
  try {
    const r = await prisma.darkSite.findUnique({ where: { id } });
    if (!r) return null;

    return {
      id: r.id,
      name: r.name,
      location: { lat: r.lat, lon: r.lon },
      lightPollution: r.lightPollution,
      description: r.description
    };
  } catch (err) {
    console.error('getDarkSiteById error:', err);
    return null;
  }
}
