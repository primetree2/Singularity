/**
 * Interface representing validated environment variables.
 */
export interface EnvConfig {
  DATABASE_URL: string;
  JWT_SECRET: string;
  API_PORT: number;
  REDIS_URL: string;
  NODE_ENV: string;
}

/**
 * Validate and load environment variables from process.env.
 *
 * @returns EnvConfig - validated environment configuration
 * @throws Error - if any required variable is missing or invalid
 */
export function validateEnv(): EnvConfig {
  const { DATABASE_URL, JWT_SECRET, API_PORT, REDIS_URL, NODE_ENV } = process.env;

  if (!DATABASE_URL) {
    throw new Error("Missing environment variable: DATABASE_URL");
  }

  if (!JWT_SECRET) {
    throw new Error("Missing environment variable: JWT_SECRET");
  }

  if (!API_PORT) {
    throw new Error("Missing environment variable: API_PORT");
  }

  const parsedPort = Number(API_PORT);
  if (!Number.isFinite(parsedPort)) {
    throw new Error("API_PORT must be a valid number");
  }

  if (!REDIS_URL) {
    throw new Error("Missing environment variable: REDIS_URL");
  }

  if (!NODE_ENV) {
    throw new Error("Missing environment variable: NODE_ENV");
  }

  return {
    DATABASE_URL,
    JWT_SECRET,
    API_PORT: parsedPort,
    REDIS_URL,
    NODE_ENV
  };
}
