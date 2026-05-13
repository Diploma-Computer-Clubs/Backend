import logging
from fastapi import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

async def redis_connection_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=503,
        content={"detail": "External cache service (Redis) connection failed. Please try again later."}
    )


async def sqlalchemy_error_handler(request: Request, exc: Exception):
    logger.error(f"Database error: {exc}")

    return JSONResponse(
        status_code=500,
        content={"detail": "Database connection error. Please try again later."}
    )