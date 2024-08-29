# app/logger.py
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.FileHandler("app_debug.log"),  # Log to a file named `app_debug.log`
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)

# Set the logging level for multipart to WARNING or higher
logging.getLogger("multipart").setLevel(logging.WARNING)

async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

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
    logger.debug(f"Request Body: {await request.body()}")  # Be cautious with large payloads or sensitive data

    # Optionally: Send error notification (email, Slack, etc.)
    # send_error_notification("Server Error Notification", error_details)

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )