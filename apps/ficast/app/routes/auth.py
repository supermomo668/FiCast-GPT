from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from ..models.request import Token
from ..services.auth import get_current_user, authenticate_user, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(
        form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Assuming authenticate_user returns a dictionary
    access_token = create_access_token(
        data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/check", response_class=JSONResponse)
async def test_auth(user=Depends(get_current_user)):
    return JSONResponse(
        status_code=200, content={"auth": "firebase", "user": user["user"]})

@router.post('/issue-api-token', response_class=JSONResponse)
async def issue_api_token(user=Depends(get_current_user)):
    access_token = create_access_token(data={"sub": user["user"]})
    return JSONResponse(
        status_code=200, content={"api_token": access_token})

@router.get("/test-api-token", response_class=JSONResponse)
async def test_api_token(user=Depends(get_current_user)):
    return JSONResponse(
        status_code=200, content={"auth": "api_key", "user": user["user"]})

