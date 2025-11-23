import { Request, Response } from 'express';

export async function getHealth(req: Request, res: Response) {
  return res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
}
