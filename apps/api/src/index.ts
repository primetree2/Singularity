import app from './server';
import { config } from './config';
import http from 'http';

const port = config.API_PORT ?? 4000;

const server: http.Server = app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`Server running on port ${port}`);
});

// Graceful shutdown helper
function shutdown(code = 0, reason?: string) {
  // eslint-disable-next-line no-console
  console.log(`Shutting down server${reason ? `: ${reason}` : ''}`);
  const timeout = setTimeout(() => {
    // Force exit if close hangs
    // eslint-disable-next-line no-console
    console.error('Forcing shutdown after timeout');
    process.exit(code);
  }, 30_000);

  server.close((err) => {
    clearTimeout(timeout);
    if (err) {
      // eslint-disable-next-line no-console
      console.error('Error during server close:', err);
      process.exit(1);
    }
    process.exit(code);
  });
}

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
  // eslint-disable-next-line no-console
  console.error('Uncaught Exception:', err);
  shutdown(1, 'uncaughtException');
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason) => {
  // eslint-disable-next-line no-console
  console.error('Unhandled Rejection:', reason);
  shutdown(1, 'unhandledRejection');
});

// Handle termination signals
process.on('SIGINT', () => shutdown(0, 'SIGINT'));
process.on('SIGTERM', () => shutdown(0, 'SIGTERM'));
