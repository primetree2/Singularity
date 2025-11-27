import { PrismaClient } from '@prisma/client';
import type { Visit } from '@singularity/shared';

const prisma = new PrismaClient();

/**
 * Create a new visit record.
 *
 * @param data - visit payload
 * @returns created Visit
 */
export async function createVisit(data: {
  userId: string;
  eventId?: string;
  darkSiteId?: string;
  photoUrl?: string;
  visibilityScore?: number;
}): Promise<Visit> {
  try {
    const created = await prisma.visit.create({
      data: {
        userId: data.userId,
        eventId: data.eventId ?? null,
        darkSiteId: data.darkSiteId ?? null,
        photoUrl: data.photoUrl ?? null,
        visibilityScore: data.visibilityScore ?? null
      }
    });

    const result: Visit = {
      id: created.id,
      userId: created.userId,
      eventId: created.eventId ?? '',
      darkSiteId: created.darkSiteId ?? '',
      timestamp: created.timestamp.toISOString(),
      photoUrl: created.photoUrl ?? '',
      visibilityScore: created.visibilityScore ?? 0,
      points: created.points
    };

    return result;
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('createVisit error:', err);
    throw err;
  }
}

/**
 * Get all visits for a given user.
 *
 * @param userId - user id
 * @returns array of Visit
 */
export async function getVisitsByUserId(userId: string): Promise<Visit[]> {
  try {
    const rows = await prisma.visit.findMany({
      where: { userId },
      orderBy: { timestamp: 'desc' }
    });

    return rows.map((r) => ({
      id: r.id,
      userId: r.userId,
      eventId: r.eventId ?? '',
      darkSiteId: r.darkSiteId ?? '',
      timestamp: r.timestamp.toISOString(),
      photoUrl: r.photoUrl ?? '',
      visibilityScore: r.visibilityScore ?? 0,
      points: r.points
    }));
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('getVisitsByUserId error:', err);
    return [];
  }
}

/**
 * Verify a visit (mark as verified).
 *
 * @param visitId - visit id
 * @returns updated Visit
 */
export async function verifyVisit(visitId: string): Promise<Visit> {
  try {
    const updated = await prisma.visit.update({
      where: { id: visitId },
      data: { verified: true }
    });

    const result: Visit = {
      id: updated.id,
      userId: updated.userId,
      eventId: updated.eventId ?? '',
      darkSiteId: updated.darkSiteId ?? '',
      timestamp: updated.timestamp.toISOString(),
      photoUrl: updated.photoUrl ?? '',
      visibilityScore: updated.visibilityScore ?? 0,
      points: updated.points
    };

    return result;
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('verifyVisit error:', err);
    throw err;
  }
}
