# services/errors.py
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
import traceback

from ..logger import log_error

def handle_task_exceptions(exc: Exception):
    """ Handle exceptions during task execution and log error details """
    log_error(f"Task error: {str(exc)}\n{traceback.format_exc()}")
    if isinstance(exc, HTTPException):
        raise exc
    raise HTTPException(status_code=500, detail="An unexpected error occurred during task execution.")

def handle_database_exceptions(db: Session, exc: Exception):
    """ Handle database-related exceptions and log error details """
    log_error(f"Database error: {str(exc)}\n{traceback.format_exc()}")
    db.rollback()  # Always rollback in case of errors to maintain consistency
    raise HTTPException(status_code=500, detail="A database error occurred.")

def handle_request_exceptions(exc: Exception):
    """ Handle exceptions raised by invalid requests and log error details """
    log_error(f"Request error: {str(exc)}\n{traceback.format_exc()}")
    if isinstance(exc, HTTPException):
        raise exc
    raise HTTPException(status_code=400, detail="Invalid request data.")
    
def generic_exception_handler(request: Request, exc: Exception):
    """ Global generic exception handler for the FastAPI app """
    log_error(f"Unhandled Exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )
