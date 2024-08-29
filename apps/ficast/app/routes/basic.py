from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from .homepage import generate_homepage_html

router = APIRouter(tags=["base"])

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

# Home route definition
@router.get("/", response_class=HTMLResponse)
async def home():
    
    html_content = generate_homepage_html()
    return HTMLResponse(content=html_content)



@router.get("/ping", response_class=JSONResponse)
async def ping():
    return JSONResponse(content={"status": True})
