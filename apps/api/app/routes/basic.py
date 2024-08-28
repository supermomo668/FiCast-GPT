from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from ..utils import get_current_user

router = APIRouter(tags=["base"])

@router.get("/", response_class=HTMLResponse)
async def home():
    html_content = """
    <html>
        <head>
            <title>FiCast-TTS Home</title>
        </head>
        <body>
            <h1>Welcome to FiCast-TTS!</h1>
            <p>Check the API documentation at <a href="/docs">/docs</a>.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/ping", 
            response_class=JSONResponse)
async def ping():
    return JSONResponse(content={"ping": "pong"})
