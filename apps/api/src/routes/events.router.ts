import { Router } from 'express';
import { getEvents, getEvent } from '../controllers/events.controller';

const router = Router();

router.get('/', getEvents);
router.get('/:id', getEvent);

export default router;
