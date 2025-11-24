import { PrismaClient } from '@prisma/client';
import type { User } from '@singularity/shared';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();
const SALT_ROUNDS = 10;

/**
 * Create a new user (hashes password before storing).
 *
 * @param email - user's email (unique)
 * @param password - plaintext password
 * @param displayName - display name
 * @returns created user (without password)
 */
export async function createUser(
  email: string,
  password: string,
  displayName: string
): Promise<User> {
  try {
    const hashed = await bcrypt.hash(password, SALT_ROUNDS);

    const created = await prisma.user.create({
      data: {
        email,
        password: hashed,
        displayName
      }
    });

    // Map Prisma user to shared User (omit password, convert dates to ISO)
    const result: User = {
      id: created.id,
      email: created.email,
      displayName: created.displayName,
      score: created.score,
      createdAt: created.createdAt.toISOString()
    };

    return result;
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('createUser error:', err);
    throw err;
  }
}

/**
 * Find user by email. Returns null if not found.
 *
 * Note: returned User omits password.
 */
export async function findUserByEmail(email: string): Promise<User | null> {
  try {
    const row = await prisma.user.findUnique({
      where: { email }
    });

    if (!row) return null;

    const user: User = {
      id: row.id,
      email: row.email,
      displayName: row.displayName,
      score: row.score,
      createdAt: row.createdAt.toISOString()
    };

    return user;
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('findUserByEmail error:', err);
    throw err;
  }
}

/**
 * Validate a plaintext password against a stored bcrypt hash.
 *
 * @returns true if matches, false otherwise
 */
export async function validatePassword(
  plainPassword: string,
  hashedPassword: string
): Promise<boolean> {
  try {
    return await bcrypt.compare(plainPassword, hashedPassword);
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('validatePassword error:', err);
    return false;
  }
}
