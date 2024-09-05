import pathlib, os

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from .homepage import generate_homepage_html

router = APIRouter(tags=["base"])

# Home route definition
@router.get("/", response_class=HTMLResponse)
async def home():
    html_content = generate_homepage_html()
    return HTMLResponse(content=html_content)

@router.get("/ping")
async def ping():
    return True

@router.get("/privacy-policy/", response_class=HTMLResponse)
async def privacy_policy():
    # Load the privacy policy content from the HTML file
    policy_path = pathlib.Path(
        os.getenv("PRIVACY_POLICY_PATH", "app/data/privacy-policy.html"))
    if policy_path.exists():
        privacy_policy_content = policy_path.read_text(encoding="utf-8")
    else:
        privacy_policy_content = "Privacy policy not found."
    return HTMLResponse(content=privacy_policy_content)
    

