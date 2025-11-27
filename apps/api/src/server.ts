import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { config } from './config';
import healthRouter from './routes/health.router';
import eventsRouter from './routes/events.router';
import darksitesRouter from './routes/darksites.router';
import usersRouter from './routes/users.router';
import notificationsRouter from './routes/notifications.router';
import gamificationRouter from './routes/gamification.router';


dotenv.config();

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());

app.use('/health', healthRouter);
app.use('/events', eventsRouter);
app.use('/darksites', darksitesRouter);
app.use('/users', usersRouter);
app.use('/notifications', notificationsRouter);
app.use('/', gamificationRouter);

export default app;
