from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from time import sleep
import json 

from ..models.db import PodcastTask
from ..models.task_status import TaskStatus

router = APIRouter()

def task_progress_stream(task_id: str, event_type: str, db: Session, interval: int = 5):
    """
    Generator that yields task progress updates as a JSON string with event fields for either script or audio.
    
    Args:
        task_id (str): The ID of the task.
        db (Session): Database session to query the task.
        event_type (str): Either "script" or "audio" to monitor task progress.
        interval (int): Time to wait (in seconds) between each status check.
    """
    while True:
        # Fetch the task status from the database
        podcast_task = db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()
        
        if not podcast_task:
            raise HTTPException(status_code=404, detail="Task not found")
        if event_type == "script":
            data = {
                "event": event_type,
                "status": podcast_task.script_status.value,
            }
            yield f"data: {json.dumps(data)}\n\n"

        elif event_type == "audio":
          data = {
              "event": event_type,
              "status": podcast_task.audio_status.value,
          }
          yield f"data: {json.dumps(data)}\n\n"

        # Delay to avoid busy waiting (polling every `interval` seconds)
        sleep(interval)

