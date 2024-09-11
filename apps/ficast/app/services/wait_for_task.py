from tenacity import retry, wait_exponential, stop_after_delay, retry_if_exception_type
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models.db import PodcastTask, TaskStatus
from ..logger import log_info, log_error
from ..utils.error_handler import TaskFailedException, TaskNotReadyException

# Retry auxiliary function with enhanced error observability
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=60),  # Exponential backoff with a cap
    stop=stop_after_delay(3600 * 24),  # Retry for up to 24 hours
    retry=retry_if_exception_type(TaskNotReadyException),  # Retry if TaskNotReadyException is raised
)
def wait_for_task_ready(db: Session, task_id: str, task_type: str) -> PodcastTask:
    """
    This function will keep retrying until the task is ready (script or audio).
    - task_type: 'script' or 'audio'
    - Raises TaskFailedException if task has failed.
    """
    podcast_task = db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()
    
    if not podcast_task:
        log_error(f"Task {task_id} not found")
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Log task status information for observability
    log_info(f"Task {task_id}: Current status (script: {podcast_task.script_status}, audio: {podcast_task.audio_status})")

    if task_type == "script":
        if podcast_task.script_status == TaskStatus.SCRIPT_CREATED:
            log_info(f"Task {task_id}: Script successfully created")
            return podcast_task
        elif podcast_task.script_status == TaskStatus.FAILURE:
            log_error(f"Task {task_id}: Script generation failed")
            raise TaskFailedException(f"Script generation failed for task {task_id}")
        else:
            log_info(f"Task {task_id}: Script generation still in progress")
            raise TaskNotReadyException(f"Script generation in progress for task {task_id}")
    
    elif task_type == "audio":
        if podcast_task.audio_status == TaskStatus.AUDIO_CREATED:
            log_info(f"Task {task_id}: Audio successfully created")
            return podcast_task
        elif podcast_task.audio_status == TaskStatus.FAILURE:
            log_error(f"Task {task_id}: Audio generation failed")
            raise TaskFailedException(f"Audio generation failed for task {task_id}")
        else:
            log_info(f"Task {task_id}: Audio generation still in progress")
            raise TaskNotReadyException(f"Audio generation in progress for task {task_id}")

    raise HTTPException(status_code=400, detail="Invalid task type requested.")
