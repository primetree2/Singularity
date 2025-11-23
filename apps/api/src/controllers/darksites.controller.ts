import { Request, Response } from 'express';
import { getNearestDarkSites } from '../services/darksite.service';

export async function getNearestDarkSitesController(req: Request, res: Response) {
  try {
    const { lat, lon, limit } = req.query;

    if (typeof lat !== 'string' || typeof lon !== 'string') {
      return res.status(400).json({ error: 'lat and lon query parameters are required and must be strings representing numbers' });
    }

    const parsedLat = Number.parseFloat(lat);
    const parsedLon = Number.parseFloat(lon);
    const parsedLimit = limit ? Number.parseInt(String(limit), 10) : 10;

    if (!Number.isFinite(parsedLat) || !Number.isFinite(parsedLon)) {
      return res.status(400).json({ error: 'lat and lon must be valid numbers' });
    }

    if (parsedLimit <= 0 || !Number.isFinite(parsedLimit)) {
      return res.status(400).json({ error: 'limit must be a positive integer' });
    }

    const results = await getNearestDarkSites(parsedLat, parsedLon, parsedLimit);

    return res.status(200).json({ items: results });
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('getNearestDarkSitesController error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
