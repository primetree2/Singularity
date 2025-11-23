import { Router } from 'express';
import { getNearestDarkSitesController } from '../controllers/darksites.controller';

const router = Router();

router.get('/nearest', getNearestDarkSitesController);

export default router;
