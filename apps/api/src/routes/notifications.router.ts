import { Router } from 'express';
import { authMiddleware } from '../middleware/auth.middleware';
import { registerToken } from '../controllers/notifications.controller';

const router = Router();

router.post('/device-token', authMiddleware, registerToken);

export default router;
