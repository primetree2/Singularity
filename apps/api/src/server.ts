import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { config } from './config';
import healthRouter from './routes/health.router';
import eventsRouter from './routes/events.router';
import darksitesRouter from './routes/darksites.router';

dotenv.config();

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());

app.use('/health', healthRouter);
app.use('/events', eventsRouter);
app.use('/darksites', darksitesRouter);

export default app;
