import { Request, Response } from 'express';
import { register, login } from '../services/users.service';

/**
 * POST /users/register
 */
export async function registerUser(req: Request, res: Response) {
  try {
    const { email, password, displayName } = req.body;

    if (!email || !password || !displayName) {
      return res.status(400).json({ error: 'email, password, and displayName are required' });
    }

    try {
      const auth = await register(email, password, displayName);
      return res.status(201).json(auth);
    } catch (err: any) {
      if (err.message?.includes('Unique constraint')) {
        return res.status(409).json({ error: 'Email already in use' });
      }
      return res.status(500).json({ error: 'Registration failed' });
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('registerUser error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

/**
 * POST /users/login
 */
export async function loginUser(req: Request, res: Response) {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'email and password are required' });
    }

    try {
      const auth = await login(email, password);
      return res.status(200).json(auth);
    } catch (err) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('loginUser error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
