# astro-service/app/main.py
"""
FastAPI entrypoint for Singularity astro-service.

Creates and wires:
- TLEManager (app.state.tle_manager)
- GeometryCalculator (app.state.geometry)
- VisibilityScorer (app.state.scorer)
- VisibilityPredictor (app.state.predictor)

Includes routers expected at:
- app.api.routes.predictions (exports `router`)
- app.api.routes.satellites (exports `router`)

Provides:
- / (health quick)
- /health
- /ready

Notes:
- Configure env var TLE_CACHE_TTL_HOURS to change cache TTL
- Configure CORS origins via ASTRO_ALLOWED_ORIGINS (comma-separated) in env
"""

import asyncio
import logging
import os
from typing import Optional

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Try to import internal modules. If your module names differ, update these imports.
try:
    from app.core.tle import TLEManager
    from app.core.geometry import GeometryCalculator
    from app.core.scoring import VisibilityScorer
    from app.core.visibility import VisibilityPredictor
except Exception as exc:
    # Provide an explicit message to help debugging missing modules
    raise ImportError("Failed to import core astro-service modules. "
                      "Ensure app.core.tle, app.core.geometry, app.core.scoring, "
                      "and app.core.visibility exist and are importable.") from exc

# Routers: these modules should expose a FastAPI `router`
predictions_router = None
satellites_router = None
try:
    # the route modules should be at app.api.routes.predictions / satellites
    from app.api.routes import predictions, satellites  # type: ignore
    predictions_router = getattr(predictions, "router", None)
    satellites_router = getattr(satellites, "router", None)
except Exception:
    # OK if imports fail here; we'll handle later when trying to include routers
    predictions_router = None
    satellites_router = None

# Optional logger configuration from your utils
try:
    from app.utils.logger import configure_logging
    configure_logging()
except Exception:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("astro-service")

SERVICE_NAME = os.environ.get("ASTRO_SERVICE_NAME", "singularity-astro-service")
SERVICE_VERSION = os.environ.get("ASTRO_SERVICE_VERSION", "0.0.1")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Singularity — Astro Service",
        description="Astronomical calculations: TLE handling, pass predictions, visibility scoring",
        version=SERVICE_VERSION,
    )

    # Configure CORS (dev: allow all; production: restrict origins)
    allowed_origins = os.environ.get("ASTRO_ALLOWED_ORIGINS", "*")
    if allowed_origins and allowed_origins != "*":
        origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]
    else:
        origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event():
        logger.info("astro-service startup: initializing components")

        # create shared components and attach to app state
        tle_ttl = int(os.environ.get("TLE_CACHE_TTL_HOURS", "6"))
        app.state.tle_manager = TLEManager(cache_ttl_hours=tle_ttl)
        app.state.geometry = GeometryCalculator()
        app.state.scorer = VisibilityScorer()
        app.state.predictor = VisibilityPredictor(
            tle_manager=app.state.tle_manager,
            geometry_calculator=app.state.geometry,
            scorer=app.state.scorer,
        )

        logger.info("Initialized TLEManager, GeometryCalculator, VisibilityScorer, VisibilityPredictor")

        # warm the TLE cache for ISS (best-effort)
        async def prefetch():
            try:
                logger.info("Prefetching ISS TLE...")
                iss = await app.state.tle_manager.get_satellite_by_name("ISS")
                if iss:
                    logger.info("ISS prefetch OK")
                else:
                    logger.warning("ISS not found in prefetch")
            except Exception as e:
                logger.warning(f"Prefetching ISS failed: {e}", exc_info=True)

        # don't block startup; schedule prefetch task
        asyncio.create_task(prefetch())

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("astro-service shutdown: cleaning up resources")
        # if any of the components implement close() or aiodisconnect close them
        tle_manager = getattr(app.state, "tle_manager", None)
        if tle_manager:
            # if TLEManager exposes any HTTP client to close, call it; catch errors
            close_fn = getattr(tle_manager, "close", None)
            if callable(close_fn):
                try:
                    maybe = close_fn()
                    # if close_fn is coroutine, await it
                    if asyncio.iscoroutine(maybe):
                        await maybe
                except Exception:
                    logger.debug("tle_manager.close() call failed or is not implemented", exc_info=True)

    # include routers if present
    if predictions_router is not None:
        try:
            app.include_router(predictions_router, prefix="/predictions", tags=["predictions"])
        except Exception as e:
            logger.warning(f"Failed to include predictions router: {e}", exc_info=True)
    else:
        logger.info("No predictions router found at app.api.routes.predictions; skipping include.")

    if satellites_router is not None:
        try:
            app.include_router(satellites_router, prefix="/satellites", tags=["satellites"])
        except Exception as e:
            logger.warning(f"Failed to include satellites router: {e}", exc_info=True)
    else:
        logger.info("No satellites router found at app.api.routes.satellites; skipping include.")

    # health endpoints
    @app.get("/", include_in_schema=False)
    async def root():
        return {"service": SERVICE_NAME, "version": SERVICE_VERSION, "status": "ok"}

    @app.get("/health")
    async def health():
        predictor = getattr(app.state, "predictor", None)
        tle_manager = getattr(app.state, "tle_manager", None)
        ready = {"service": SERVICE_NAME, "version": SERVICE_VERSION}
        ready["predictor"] = "ready" if predictor is not None else "missing"
        ready["tle_manager"] = "ready" if tle_manager is not None else "missing"
        ready["status"] = "ok" if predictor and tle_manager else "degraded"
        return ready

    @app.get("/ready")
    async def ready():
        tle_manager = getattr(app.state, "tle_manager", None)
        resp = {"ready": True, "details": {}}
        if tle_manager is None:
            resp["ready"] = False
            resp["details"]["tle_manager"] = "missing"
        else:
            resp["details"]["tle_manager"] = "present"
        return resp

    # generic error handler returning JSON
    @app.exception_handler(Exception)
    async def generic_exc_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception during request", exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


# helper dependency for routers that need the predictor
def get_predictor(request: Request) -> Optional[VisibilityPredictor]:
    return getattr(request.app.state, "predictor", None)


# Export app for Uvicorn/Gunicorn
app = create_app()

# Allow running directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
