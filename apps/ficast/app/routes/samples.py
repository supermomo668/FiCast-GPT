import os
import json
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/samples",
    tags=["samples"]
)

# Define the file paths
AUDIO_SAMPLE_PATH = os.getenv("AUDIO_SAMPLE_PATH", "app/data/samples/dialogue.wav")
SCRIPT_SAMPLE_PATH = os.getenv("SCRIPT_SAMPLE_PATH", "app/data/samples/script.json")

@router.get("/audio", response_class=FileResponse)
async def get_sample_audio():
    if not os.path.exists(AUDIO_SAMPLE_PATH):
        raise HTTPException(status_code=404, detail="Sample audio not found")
    
    return FileResponse(path=AUDIO_SAMPLE_PATH, media_type="audio/wav")

@router.get("/script", response_class=Response)
async def get_sample_script():
    if not os.path.exists(SCRIPT_SAMPLE_PATH):
        raise HTTPException(status_code=404, detail="Sample script not found")
    
    try:
        with open(SCRIPT_SAMPLE_PATH, 'r') as f:
            script = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load script: {str(e)}")
    
    return Response(content=json.dumps(script), media_type="application/json")

@router.get(
  "/script-dialogue", response_class=Response)
async def get_sample_dialogue():
    if not os.path.exists(SCRIPT_SAMPLE_PATH):
        raise HTTPException(status_code=404, detail="Sample script not found")

    try:
        with open(SCRIPT_SAMPLE_PATH, 'r') as f:
            script = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load script: {str(e)}")

    # Extract the "dialogues" key
    dialogues = script.get("dialogues", None)
    if dialogues is None:
        raise HTTPException(status_code=404, detail="Dialogues not found in script")

    return Response(content=json.dumps(dialogues), media_type="application/json")
