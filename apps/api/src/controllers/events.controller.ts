import { Request, Response } from 'express';
import { listEvents, getEventById } from '../services/events.service';

/**
 * GET /events
 */
export async function getEvents(req: Request, res: Response) {
  try {
    const { startDate, endDate, lat, lon } = req.query;

    const events = await listEvents({
      startDate: typeof startDate === 'string' ? startDate : undefined,
      endDate: typeof endDate === 'string' ? endDate : undefined,
      lat: lat ? Number(lat) : undefined,
      lon: lon ? Number(lon) : undefined
    });

    return res.status(200).json({ events });
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('getEvents error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

/**
 * GET /events/:id
 */
export async function getEvent(req: Request, res: Response) {
  try {
    const { id } = req.params;

    const event = await getEventById(id);
    if (!event) {
      return res.status(404).json({ error: 'Event not found' });
    }

    return res.status(200).json({ event });
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('getEvent error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
