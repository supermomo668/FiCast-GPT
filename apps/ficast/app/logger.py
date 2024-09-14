# app/logger.py
import logging
import os
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback

USE_CELERY = os.getenv("USE_CELERY", "false").lower() in ("true", "1")

# Create the logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG

# Create handlers for file and stream logging
file_handler = logging.FileHandler("app.log")
stream_handler = logging.StreamHandler()

# Set the level for each handler
file_handler.setLevel(logging.DEBUG)
stream_handler.setLevel(logging.DEBUG)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Prevent propagation to the root logger if you don't want duplicate logs
logger.propagate = False

# Set the logging level for multipart to WARNING or higher
logging.getLogger("multipart").setLevel(logging.WARNING)

# Middleware logging request and response
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Exception handlers
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": str(exc)}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

async def generic_exception_handler(request: Request, exc: Exception):
    error_details = f"Unhandled Exception: {str(exc)}\n{traceback.format_exc()}"
    logger.error(error_details)
    logger.debug(f"Request URL: {request.url}")
    logger.debug(f"Request Headers: {request.headers}")
    logger.debug(f"Request Body: {await request.body()}")

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )

# Helper logging functions for custom logging
if not USE_CELERY:
    import threading
    lock = threading.Lock()

def log_info(msg):
    if not USE_CELERY:
        with lock:
            logger.info(msg)
    else:
        logger.info(msg)

def log_error(msg):
    if not USE_CELERY:
        with lock:
            logger.error(msg)
    else:
        logger.error(msg)
