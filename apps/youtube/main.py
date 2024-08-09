import os
from pydantic import BaseModel
from typing import Optional, List
import dotenv

from fastapi import FastAPI, HTTPException, UploadFile, File, Form

from services.upload_video import get_authenticated_service, initialize_upload


dotenv.load_dotenv()

app = FastAPI()

class VideoUploadRequest(BaseModel):
    title: str
    description: str
    category: str
    keywords: Optional[str] = ''
    privacy_status: str

@app.post("/upload_video")
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    keywords: Optional[str] = Form(''),
    privacy_status: str = Form('private')
):
    try:
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        
        youtube = get_authenticated_service()

        initialize_upload(
            youtube,
            file_path=file_location,
            title=title,
            description=description,
            category=category,
            keywords=keywords,
            privacy_status=privacy_status
        )
        
        return {"message": "Video uploaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(file_location):
            os.remove(file_location)
