import { PrismaClient } from '@prisma/client';
import type { DeviceToken as SharedDeviceToken } from '@singularity/shared';

const prisma = new PrismaClient();

function validatePlatform(platform: string): 'web' | 'android' {
  const p = platform?.toLowerCase();
  if (p === 'web') return 'web';
  if (p === 'android') return 'android';
  throw new Error('Invalid platform: must be "web" or "android"');
}

export async function registerDeviceToken(
  userId: string,
  token: string,
  platform: string
): Promise<SharedDeviceToken> {
  try {
    const normalized = validatePlatform(platform);

    const existing = await prisma.deviceToken.findFirst({
      where: { userId, token }
    });

    if (existing) {
      const updated = await prisma.deviceToken.update({
        where: { id: existing.id },
        data: { platform: normalized }
      });

      return {
        id: updated.id,
        userId: updated.userId,
        token: updated.token,
        platform: updated.platform as 'web' | 'android',
        createdAt: updated.createdAt.toISOString()
      };
    }

    const created = await prisma.deviceToken.create({
      data: {
        userId,
        token,
        platform: normalized
      }
    });

    return {
      id: created.id,
      userId: created.userId,
      token: created.token,
      platform: created.platform as 'web' | 'android',
      createdAt: created.createdAt.toISOString()
    };
  } catch (err) {
    console.error('registerDeviceToken error:', err);
    throw err;
  }
}

export async function getDeviceTokensByUserId(
  userId: string
): Promise<SharedDeviceToken[]> {
  try {
    const rows = await prisma.deviceToken.findMany({
      where: { userId }
    });

    return rows.map((r) => ({
      id: r.id,
      userId: r.userId,
      token: r.token,
      platform: (r.platform === 'web' || r.platform === 'android'
        ? r.platform
        : 'web') as 'web' | 'android',
      createdAt: r.createdAt.toISOString()
    }));
  } catch (err) {
    console.error('getDeviceTokensByUserId error:', err);
    return [];
  }
}

export async function sendPushNotification(
  userId: string,
  title: string,
  body: string
): Promise<void> {
  try {
    const tokens = await getDeviceTokensByUserId(userId);

    for (const t of tokens) {
      console.log(
        `Push → user=${userId}, token=${t.token}, platform=${t.platform} :: ${title} - ${body}`
      );
    }

    // TODO: integrate actual push (web-push or FCM)
  } catch (err) {
    console.error('sendPushNotification error:', err);
    throw err;
  }
}
