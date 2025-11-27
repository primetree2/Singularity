import { Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { createVisit } from '../models/visit.model';
import {
  awardPoints,
  checkAndAwardBadges,
  getUserBadges
} from '../services/gamification.service';
import { computeVisibility } from '../services/visibility.service';
import type { Visit as SharedVisit, Badge as SharedBadge, LeaderboardEntry, User as SharedUser } from '@singularity/shared';

const prisma = new PrismaClient();

/**
 * Report a visit to an event or darksite.
 */
export async function reportVisit(req: Request, res: Response) {
  try {
    const userPayload = (req as any).user;
    const userId = userPayload?.sub || userPayload?.id || userPayload?.userId;
    if (!userId || typeof userId !== 'string') {
      return res.status(400).json({ error: 'Authenticated user id is required' });
    }

    const { eventId, darkSiteId, lat, lon, photoUrl } = req.body;

    if (!eventId && !darkSiteId) {
      return res.status(400).json({ error: 'Either eventId or darkSiteId must be provided' });
    }

    // Determine coordinates for visibility calculation
    let coordLat: number | undefined = typeof lat === 'number' ? lat : undefined;
    let coordLon: number | undefined = typeof lon === 'number' ? lon : undefined;

    if ((coordLat === undefined || coordLon === undefined) && darkSiteId) {
      const ds = await prisma.darkSite.findUnique({ where: { id: darkSiteId } });
      if (ds) {
        coordLat = ds.lat;
        coordLon = ds.lon;
      }
    }

    if ((coordLat === undefined || coordLon === undefined) && eventId) {
      const ev = await prisma.event.findUnique({ where: { id: eventId } });
      if (ev) {
        coordLat = ev.lat;
        coordLon = ev.lon;
      }
    }

    if (coordLat === undefined || coordLon === undefined) {
      return res.status(400).json({ error: 'Latitude and longitude are required (either directly or via event/darkSite)' });
    }

    // Compute visibility
    const vis = await computeVisibility({ lat: coordLat, lon: coordLon, time: new Date() });
    const visibilityScore = vis?.score ?? 0;

    // Calculate points: base 10 + (visibilityScore / 10) rounded
    const points = 10 + Math.round(visibilityScore / 10);

    // Create visit record
    const visit = await createVisit({
      userId,
      eventId,
      darkSiteId,
      photoUrl,
      visibilityScore
    });

    // Award points and check badges
    await awardPoints(userId, points);
    const newlyEarned = await checkAndAwardBadges(userId);

    return res.status(201).json({
      visit,
      pointsAwarded: points,
      newlyEarnedBadges: newlyEarned
    });
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('reportVisit error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

/**
 * Get badges for a user (by userId param).
 */
export async function getUserBadgesController(req: Request, res: Response) {
  try {
    const { id: userId } = req.params;
    if (!userId || typeof userId !== 'string') {
      return res.status(400).json({ error: 'userId param is required' });
    }

    const badges = await getUserBadges(userId);
    return res.status(200).json({ items: badges });
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('getUserBadgesController error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

/**
 * Get leaderboard (top users by score).
 */
export async function getLeaderboard(req: Request, res: Response) {
  try {
    const limit = req.query.limit ? Number(req.query.limit) : 100;
    const take = Number.isFinite(limit) && limit > 0 ? Math.min(limit, 1000) : 100;

    const users = await prisma.user.findMany({
      orderBy: { score: 'desc' },
      take
    });

    const leaderboard: LeaderboardEntry[] = users.map((u, idx) => {
      const user: SharedUser = {
        id: u.id,
        email: u.email,
        displayName: u.displayName,
        score: u.score,
        createdAt: u.createdAt.toISOString()
      };

      return {
        rank: idx + 1,
        user,
        score: u.score
      } as LeaderboardEntry;
    });

    return res.status(200).json({ items: leaderboard, total: leaderboard.length });
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('getLeaderboard error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
