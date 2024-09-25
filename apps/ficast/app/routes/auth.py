from typing import Optional
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from ..logger import logger
from ..models.auth import TokenIssueModel, AdminTokenIssueModel, AccessLevelEnum, AccessLevelModel, TokenSourceModel, UserAuthenticationResponse
from ..services.auth import get_current_user, authenticate_user, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login-access-token", response_model=TokenIssueModel)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    access_level: AccessLevelEnum = AccessLevelEnum.ADMIN,  # Default admin access level
    expire_delta: Optional[timedelta] = None  # Optional duration override
):
    user_info = authenticate_user(form_data.username, form_data.password)
    if not user_info:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    # Create the token with access level and expiration
    access_token = create_access_token(
        username=user_info.username,
        access_level=access_level,
        expires_delta=expire_delta
    )
    return TokenIssueModel(
        access_token=access_token,
        token_type=TokenSourceModel.BEARER,
        access_level=access_level,
        expires_in=expire_delta
    )

@router.post("/check", response_class=JSONResponse)
async def test_auth(
    user_auth: UserAuthenticationResponse=Depends(get_current_user)):
    return JSONResponse(
        status_code=200, content=user_auth.model_dump()
    )

@router.post('/issue-api-token', response_model=TokenIssueModel)
async def issue_api_token(
    user_auth:UserAuthenticationResponse=Depends(get_current_user),
    access_level: AccessLevelEnum = AccessLevelEnum.FREEMIUM
    ):
    # Get access level default settings
    """
    Issues an API token with the given access level and expiration duration.
    Args:
        user: The user to issue the token for.
        access_level: The access level of the token

    Returns:
        An `APITokenResponseModel` containing the issued API token and its access level.
    """
    # Create the token
    access_token = create_access_token(
        username=user_auth.username,
        access_level=access_level,
    )
    logger.info(f"Access token issued for user: {user_auth.username} with access level: {access_level}")
    return TokenIssueModel(
        access_token=access_token,
        access_level=access_level
    )

@router.post("/test-api-token")
async def test_api_token(
    user_auth:UserAuthenticationResponse=Depends(get_current_user)):
    return UserAuthenticationResponse(
        username= user_auth.username,
        auth_source=user_auth.auth_source
    )

