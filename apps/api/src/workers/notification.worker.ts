// TODO: Install bullmq: pnpm add bullmq
// TODO: Requires Redis connection (REDIS_URL env)

/**
 * Process a notification job.
 *
 * For now this is a stub that logs job data and simulates delivery.
 * TODO: Integrate actual notification service (web-push / FCM) here.
 */
export async function processNotificationJob(job: any): Promise<void> {
  try {
    // Log incoming job payload
    // job.data is expected to contain { userId, title, body, meta? }
    // eslint-disable-next-line no-console
    console.log('Processing notification job:', JSON.stringify(job?.data));

    // Simulate work (e.g., call sendPushNotification)
    await new Promise((resolve) => setTimeout(resolve, 200));

    // eslint-disable-next-line no-console
    console.log('Notification processing simulated for user:', job?.data?.userId);
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('Error processing notification job:', err);
    throw err;
  }
}

/*
  Example BullMQ worker setup (commented out until bullmq is installed and Redis is configured):

  import { Worker } from 'bullmq';
  import { processNotificationJob } from './notification.worker';
  const connection = { connection: { url: process.env.REDIS_URL } };

  // Create a worker that will process jobs from the "notifications" queue
  const worker = new Worker('notifications', async (job) => {
    await processNotificationJob(job);
  }, connection);

  worker.on('completed', (job) => {
    console.log(`Job ${job.id} completed`);
  });

  worker.on('failed', (job, err) => {
    console.error(`Job ${job?.id} failed`, err);
  });

  // Note: ensure Redis is available and REDIS_URL is set in environment variables
*/
