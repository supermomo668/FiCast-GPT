# services/exceptions.py

from fastapi import HTTPException

class TaskNotFoundException(HTTPException):
    def __init__(self, task_id: str):
        super().__init__(status_code=404, detail=f"Task {task_id} not found")

class TaskAlreadyExistsException(HTTPException):
    def __init__(self, task_id: str):
        super().__init__(status_code=400, detail=f"Task {task_id} already exists")

class InvalidTaskStatusException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)
