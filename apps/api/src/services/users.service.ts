import jwt from 'jsonwebtoken';
import { PrismaClient } from '@prisma/client';
import { config } from '../config';
import { createUser, findUserByEmail, validatePassword } from '../models/user.model';
import type { AuthResponse } from '@singularity/shared';

const prisma = new PrismaClient();
const TOKEN_EXPIRES_IN = '7d';
const TOKEN_EXPIRES_IN_SECONDS = 7 * 24 * 60 * 60; // 7 days

/**
 * Register a new user and return auth response.
 */
export async function register(
  email: string,
  password: string,
  displayName: string
): Promise<AuthResponse> {
  try {
    const user = await createUser(email, password, displayName);

    const token = jwt.sign(
      { sub: user.id, email: user.email },
      config.JWT_SECRET,
      { expiresIn: TOKEN_EXPIRES_IN }
    );

    return {
      token,
      user,
      expiresIn: TOKEN_EXPIRES_IN_SECONDS
    };
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('register error:', err);
    throw new Error('Registration failed');
  }
}

/**
 * Login an existing user and return auth response.
 */
export async function login(email: string, password: string): Promise<AuthResponse> {
  try {
    // Use the model helper to get the public user (may not include password)
    const user = await findUserByEmail(email);
    if (!user) {
      throw new Error('Invalid credentials');
    }

    // Fetch the raw user row to obtain hashed password for validation
    const dbUser = await prisma.user.findUnique({ where: { email } });
    if (!dbUser || !dbUser.password) {
      throw new Error('Invalid credentials');
    }

    const valid = await validatePassword(password, dbUser.password);
    if (!valid) {
      throw new Error('Invalid credentials');
    }

    const token = jwt.sign(
      { sub: user.id, email: user.email },
      config.JWT_SECRET,
      { expiresIn: TOKEN_EXPIRES_IN }
    );

    return {
      token,
      user,
      expiresIn: TOKEN_EXPIRES_IN_SECONDS
    };
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('login error:', err);
    throw new Error('Authentication failed');
  } finally {
    // Note: do not disconnect Prisma here to allow re-use elsewhere
  }
}
