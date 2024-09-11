from fastapi import HTTPException

class TaskNotReadyException(Exception):
    pass

class TaskFailedException(Exception):
    pass

def handle_task_exceptions(e: Exception):
    """
    Handles common task-related exceptions and returns an appropriate HTTPException.

    Args:
        e (Exception): The exception to handle.
    Raises:
        HTTPException: An appropriate HTTPException based on the exception type.
    """
    if isinstance(e, TaskFailedException):
        raise HTTPException(status_code=500, detail=f"Task failed: {str(e)}")
    
    elif isinstance(e, TaskNotReadyException):
        raise HTTPException(status_code=202, detail=f"Task in progress: {str(e)}")
    
    elif isinstance(e, HTTPException):
        raise e  # Re-raise HTTPException directly to keep original status code and detail
    else:
        # Catch all other exceptions and return a 500 Internal Server Error
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
