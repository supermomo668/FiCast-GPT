from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..models import PodcastRequest
from ..services import generate_podcast_audio, generate_podcast_script
from ..utils import get_current_user

router = APIRouter(
    prefix="/podcast",
    tags=["podcast"]
)

@router.post("/generate-audio")
async def create_podcast_audio(request: PodcastRequest, user=Depends(get_current_user)):
    audio = await generate_podcast_audio(request)
    return audio

@router.post("/generate-script")
async def create_podcast_script(request: PodcastRequest, user=Depends(get_current_user)):
    script = await generate_podcast_script(request)
    return script
