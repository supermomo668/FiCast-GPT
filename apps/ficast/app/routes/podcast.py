from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ficast.conversation.podcast import Podcast

from ..models.db import PodcastTask, TaskStatus
from ..models.session import get_db

from ..tasks.task import Task
from ..models.request import PodcastRequest
from ..models.response import TaskCreate, TaskStatusResponse
from ..utils import get_current_user

router = APIRouter(
    prefix="/podcast",
    tags=["podcast"]
)

@router.post("/create", response_model=TaskCreate)
async def create_podcast(
    request: PodcastRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    task = Task(db)
    try:
        task_msg = task.create_podcast(request)
        return TaskCreate(**task_msg)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_podcast_status(task_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    podcast_task = db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()
    
    if not podcast_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(
        script_status=podcast_task.script_status, audio_status=podcast_task.audio_status
    )

@router.get("/{task_id}/script", response_class=Response)
async def get_podcast_script(task_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    podcast_task = db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()

    if not podcast_task:
        raise HTTPException(status_code=404, detail="Podcast task not found")

    if podcast_task.script_status == TaskStatus.FAILURE:
        raise HTTPException(status_code=500, detail="Script generation failed")

    if podcast_task.script_status != TaskStatus.SUCCESS:
        raise HTTPException(status_code=202, detail="Script generation in progress")

    return Response(content=podcast_task.script, media_type="application/json")

@router.post("/{task_id}/audio", response_model=TaskCreate)
async def create_podcast_audio(task_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        # Fetch the existing podcast task using the db session
        podcast_task = db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()
        
        if not podcast_task:
            raise HTTPException(status_code=404, detail="Podcast task not found")
        
        if podcast_task.script_status != TaskStatus.SUCCESS or not podcast_task.script:
            raise HTTPException(status_code=400, detail="Script must be generated before audio can be created")

        # Now generate the audio using the existing task and session
        task = Task(db=db, task_id=task_id)  # Reuse the existing task_id
        task_msg = task.generate_audio()
        return TaskCreate(**task_msg)
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/{task_id}/audio", response_class=Response)
async def get_podcast_audio(task_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    podcast_task = db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()

    if not podcast_task:
        raise HTTPException(status_code=404, detail="Audio task not found")

    if podcast_task.audio_status == TaskStatus.FAILURE:
        raise HTTPException(status_code=500, detail="Audio generation failed")

    if podcast_task.audio_status != TaskStatus.SUCCESS:
        raise HTTPException(status_code=202, detail="Audio generation in progress")

    if not podcast_task.audio:
        raise HTTPException(status_code=404, detail="Audio not found")

    return Response(
        content=podcast_task.audio, media_type="audio/wav")
