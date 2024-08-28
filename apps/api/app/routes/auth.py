from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from ..models.request import Token
from ..utils import get_current_user, authenticate_user, create_access_token

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

@router.get("/verify-token", response_class=JSONResponse)
async def verify_token(user=Depends(get_current_user)):
    return JSONResponse(
        content={
            "status": "success", "user": user["user"]}
    )