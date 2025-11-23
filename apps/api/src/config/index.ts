import { validateEnv, EnvConfig } from './env.schema';

let config: EnvConfig;

try {
  config = validateEnv();
} catch (err) {
  console.error('Environment validation error:', err instanceof Error ? err.message : err);
  process.exit(1);
}

export { config };
