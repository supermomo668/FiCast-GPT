from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ficast.conversation.podcast import Podcast

from ..models.db import PodcastTask, TaskStatus
from ..models.session import get_db

from ..tasks import Task
from ..models.request import PodcastRequest
from ..utils import get_current_user

router = APIRouter(
    prefix="/podcast",
    tags=["podcast"]
)

@router.post("/create", response_model=str)
async def create_podcast(
    request: PodcastRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    task = Task(db)
    task_id = task.create_podcast(request)
    return task_id

@router.get("/{task_id}/status", response_model=dict)
async def get_podcast_status(task_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    task = Task(db)
    podcast_task = task.db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()
    if not podcast_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "script_status": podcast_task.status,
        "audio_status": podcast_task.is_audio_task
    }

@router.get("/{task_id}/script", response_class=JSONResponse)
async def get_podcast_script(task_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    task = Task(db)
    podcast_task = task.db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()

    if not podcast_task:
        raise HTTPException(status_code=404, detail="Podcast not found")

    # Wait until the script task is completed
    while podcast_task.status != TaskStatus.SUCCESS:
        if podcast_task.status == TaskStatus.FAILURE:
            raise HTTPException(status_code=500, detail="Task failed")
        if podcast_task.status in [TaskStatus.PENDING, TaskStatus.STARTED]:
            podcast_task = task.db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()
        else:
            raise HTTPException(status_code=400, detail=f"Unexpected status: {podcast_task.status}")

    return podcast_task.script

@router.post("/{task_id}/audio", response_model=str)
async def create_podcast_audio(task_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    task = Task(db)

    # Ensure the script generation task is complete and script is available
    podcast_task = task.db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()
    if not podcast_task:
        raise HTTPException(status_code=404, detail="Podcast task not found")
    
    if podcast_task.status != TaskStatus.SUCCESS or not podcast_task.script:
        raise HTTPException(status_code=400, detail="Script must be generated before audio can be created")

    # Now generate the audio
    audio_id = task.generate_audio()
    return audio_id

@router.get("/{task_id}/audio", response_class=Response)
async def get_podcast_audio(task_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    task = Task(db)
    podcast_task = task.db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()

    if not podcast_task:
        raise HTTPException(status_code=404, detail="Audio task not found")

    # Ensure the script generation task is complete before attempting to retrieve audio
    if podcast_task.status != TaskStatus.SUCCESS or not podcast_task.script:
        raise HTTPException(status_code=400, detail="Script must be generated before audio can be retrieved")

    # Wait until the audio task is completed
    while podcast_task.is_audio_task != TaskStatus.SUCCESS:
        if podcast_task.is_audio_task == TaskStatus.FAILURE:
            raise HTTPException(status_code=500, detail="Audio task failed")
        if podcast_task.is_audio_task in [TaskStatus.PENDING, TaskStatus.STARTED]:
            podcast_task = task.db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()
        else:
            raise HTTPException(status_code=400, detail=f"Unexpected status: {podcast_task.is_audio_task}")

    if not podcast_task.audio:
        raise HTTPException(status_code=404, detail="Audio not found")

    return Response(content=podcast_task.audio, media_type="audio/wav")
