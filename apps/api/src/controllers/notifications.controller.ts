import { Request, Response } from 'express';
import { registerDeviceToken } from '../services/notifications.service';

export async function registerToken(req: Request, res: Response) {
  try {
    const user = (req as any).user;
    const userId = user?.sub || user?.id || user?.userId;

    if (!userId || typeof userId !== 'string') {
      return res.status(400).json({ error: 'Authenticated user id is required' });
    }

    const { token, platform } = req.body;

    if (!token || typeof token !== 'string') {
      return res.status(400).json({ error: 'token is required and must be a string' });
    }

    if (!platform || typeof platform !== 'string') {
      return res.status(400).json({ error: 'platform is required and must be a string' });
    }

    const device = await registerDeviceToken(userId, token, platform);

    return res.status(201).json(device);
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('registerToken error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
