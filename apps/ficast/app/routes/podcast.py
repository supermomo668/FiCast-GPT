# routes/podcast.py
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from ..models.request import TaskRequest, PodcastRequest
from ..models.task_status import TaskProgressRequest, TaskStatusUpdate, TaskStatusResponse

from ..models.db import PodcastTask
from ..models.session import get_db
from ..logger import log_info
from ..tasks.task import Task
from ..services.wait_for_task import wait_for_task_ready
from ..services.task_status_stream import task_progress_stream
from ..services.auth import get_current_user
from ..services.errors import handle_task_exceptions, handle_database_exceptions, handle_request_exceptions

router = APIRouter(
    prefix="/podcast",
    tags=["podcast"]
)

@router.post("/create-script", response_model=TaskStatusUpdate)
async def create_podcast(request: PodcastRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    task = Task(db)
    try:
        log_info(f"Creating podcast for user {user.username} with request: {request}")
        task_msg: TaskStatusUpdate = task.create_podcast(request)
        return TaskStatusUpdate(**task_msg.model_dump())
    except Exception as e:
        handle_task_exceptions(e)

@router.post("/stream/progress")
async def stream_task_progress(request: TaskProgressRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Stream task progress updates (script/audio) as Server-Sent Events (SSE).
    """
    log_info(f"Streaming task progress: {request}")
    try:
        return StreamingResponse(
            task_progress_stream(request.task_id, request.event_type, db), 
            media_type="text/event-stream"
        )
    except Exception as e:
        handle_task_exceptions(e)

@router.post("/status", response_model=TaskStatusResponse)
async def get_podcast_status(request: TaskProgressRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        podcast_task = db.query(PodcastTask).filter(PodcastTask.task_id == request.task_id).first()
        if not podcast_task:
            raise HTTPException(status_code=404, detail=f"Task {request.task_id} not found")
        
        status = {
            "script_status": podcast_task.script_status,
            "audio_status": podcast_task.audio_status,
            "error": podcast_task.error_message
        }
        return TaskStatusResponse(**status)
    except Exception as e:
        handle_database_exceptions(db, e)

@router.post("/script", response_class=JSONResponse)
async def get_podcast_script(request: TaskRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        podcast_task = wait_for_task_ready(db, request.task_id, "script")
        return JSONResponse(status_code=200, content=podcast_task.script)
    except Exception as e:
        handle_task_exceptions(e)

@router.post("/create-audio", response_model=TaskStatusUpdate)
async def create_podcast_audio(request: TaskRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    log_info(f"Creating podcast audio for user {user.username} with request: {request}")
    try:
        podcast_task = db.query(PodcastTask).filter(PodcastTask.task_id == request.task_id).first()
        if not podcast_task:
            raise HTTPException(status_code=404, detail="Podcast task not found")
        if podcast_task.script_status != TaskStatus.SCRIPT_CREATED:
            raise HTTPException(status_code=400, detail="Script must be generated before audio can be created")
        
        task = Task(db=db, task_id=request.task_id)
        task_msg: TaskStatusUpdate = task.generate_audio()
        return TaskStatusUpdate(**task_msg.model_dump())
    except Exception as e:
        handle_task_exceptions(e)

@router.post("/audio", response_class=Response)
async def get_podcast_audio(request: TaskRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        podcast_task = wait_for_task_ready(db, request.task_id, "audio")
        if not podcast_task.audio:
            raise HTTPException(status_code=404, detail="Audio not found")
        return Response(content=podcast_task.audio, media_type="audio/wav")
    except Exception as e:
        handle_task_exceptions(e)
