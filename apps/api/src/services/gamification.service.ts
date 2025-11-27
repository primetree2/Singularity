import { PrismaClient } from '@prisma/client';
import type { Badge } from '@singularity/shared';

const prisma = new PrismaClient();

/**
 * Add points to a user's score.
 */
export async function awardPoints(userId: string, points: number): Promise<void> {
  try {
    await prisma.user.update({
      where: { id: userId },
      data: { score: { increment: points } }
    });
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('awardPoints error:', err);
    throw err;
  }
}

/**
 * Check which badges user should earn based on score.
 * Creates UserBadge entries for newly earned badges.
 *
 * @returns array of newly earned badges
 */
export async function checkAndAwardBadges(userId: string): Promise<Badge[]> {
  try {
    const user = await prisma.user.findUnique({
      where: { id: userId }
    });

    if (!user) return [];

    const userScore = user.score;

    // Get all badges
    const allBadges = await prisma.badge.findMany();

    // Get already earned badge IDs
    const earned = await prisma.userBadge.findMany({
      where: { userId },
      select: { badgeId: true }
    });
    const earnedIds = new Set(earned.map((e) => e.badgeId));

    // Filter badges that user qualifies for but hasn't earned yet
    const newlyEarned = allBadges.filter(
      (b) => userScore >= b.pointsRequired && !earnedIds.has(b.id)
    );

    // Create UserBadge records for each
    for (const badge of newlyEarned) {
      await prisma.userBadge.create({
        data: {
          userId,
          badgeId: badge.id
        }
      });
    }

    // Return newly earned badge objects in shared format
    return newlyEarned.map((b) => ({
      id: b.id,
      name: b.name,
      description: b.description,
      iconUrl: b.iconUrl,
      earnedAt: new Date().toISOString()
    }));
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('checkAndAwardBadges error:', err);
    throw err;
  }
}

/**
 * Get all badges earned by a user.
 */
export async function getUserBadges(userId: string): Promise<Badge[]> {
  try {
    const rows = await prisma.userBadge.findMany({
      where: { userId },
      include: { badge: true },
      orderBy: { earnedAt: 'desc' }
    });

    return rows.map((r) => ({
      id: r.badge.id,
      name: r.badge.name,
      description: r.badge.description,
      iconUrl: r.badge.iconUrl,
      earnedAt: r.earnedAt.toISOString()
    }));
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('getUserBadges error:', err);
    return [];
  }
}
