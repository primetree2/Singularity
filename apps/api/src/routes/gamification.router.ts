import { Router } from 'express';
import { authMiddleware } from '../middleware/auth.middleware';
import {
  reportVisit,
  getUserBadgesController,
  getLeaderboard
} from '../controllers/gamification.controller';

const router = Router();

router.post('/visits', authMiddleware, reportVisit);
router.get('/users/:userId/badges', getUserBadgesController);
router.get('/leaderboard', getLeaderboard);

export default router;
