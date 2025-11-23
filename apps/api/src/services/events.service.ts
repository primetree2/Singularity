import { PrismaClient } from '@prisma/client';
import type { Event } from '@singularity/shared';
import { formatEvent } from '@singularity/shared';

const prisma = new PrismaClient();

/**
 * List events with optional date filters.
 *
 * @param filters - optional filtering options
 * @returns Promise<Event[]>
 */
export async function listEvents(filters?: {
  startDate?: string;
  endDate?: string;
  lat?: number;
  lon?: number;
}): Promise<Event[]> {
  try {
    const where: any = {};

    if (filters?.startDate || filters?.endDate) {
      where.AND = [];
      if (filters.startDate) {
        where.AND.push({
          start: {
            gte: new Date(filters.startDate)
          }
        });
      }
      if (filters.endDate) {
        where.AND.push({
          end: {
            lte: new Date(filters.endDate)
          }
        });
      }
    }

    // Note: lat/lon filtering (proximity) is more complex and typically done with geo queries.
    // For now we fetch by date filters; future: integrate PostGIS or manual Haversine filtering.

    const rows = await prisma.event.findMany({
      where,
      orderBy: { start: 'asc' }
    });

    // Map DB rows to shared Event shape using shared formatter
    return rows.map((r) => formatEvent(r));
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('listEvents error:', err);
    return [];
  }
}

/**
 * Get a single event by id.
 *
 * @param id - event id
 * @returns Promise<Event | null>
 */
export async function getEventById(id: string): Promise<Event | null> {
  try {
    const row = await prisma.event.findUnique({
      where: { id }
    });

    if (!row) return null;
    return formatEvent(row);
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('getEventById error:', err);
    return null;
  }
}
