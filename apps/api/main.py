"""FastAPI application entrypoint."""

import logging

from fastapi import FastAPI

from apps.api.routes import health , investigations , repositories
from codepilot.config.logging import configure_logging
from codepilot.config.settings import get_settings

configure_logging()
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(health.router)
app.include_router(investigations.router)



logger.info("%s starting up (environment=%s)", settings.app_name, settings.environment)
