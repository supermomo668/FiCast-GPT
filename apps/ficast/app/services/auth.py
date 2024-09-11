import os
import base64
from re import U
import secrets
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

from fastapi import Depends, Header, Security, HTTPException, Request, status
from fastapi.security import HTTPBasic, APIKeyHeader

from firebase_admin import credentials, auth
import firebase_admin

from ..models.auth import AccessLevelEnum, AccessLevelModel, TokenEncodingModel, UserAuthenticationResponse, TokenSourceModel
from ..logger import logger
from ..utils.startup import load_env_credentials

# Load environment variables
from dotenv import load_dotenv
load_dotenv(".env")

# Load environment variables
JWT_SECRET_KEY = str(os.getenv("JWT_SECRET_KEY"))
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES", 60*24*7))
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

assert FIREBASE_CREDENTIALS_PATH, "FIREBASE_CREDENTIALS_PATH environment variable must be set"

# Initialize Firebase Admin SDK
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

# Security objects for Basic Auth and API Key
security = HTTPBasic()
auth_header = "Authorization"
api_key_header = APIKeyHeader(
  name=auth_header, auto_error=False)

def verify_user(username: str, password: str) -> bool:
    creds = load_env_credentials()
    correct_username = secrets.compare_digest(username, creds["username"])
    correct_password = secrets.compare_digest(password, creds["password"])
    return correct_username and correct_password

def create_access_token(
    username: str, 
    access_level: AccessLevelEnum = AccessLevelEnum.FREEMIUM, expires_delta: Optional[timedelta] = None
) -> str:
    # Get default access level settings
    if not expires_delta:
        expires_delta = AccessLevelModel.get_access_level_info(access_level).token_duration
    # Token payload
    to_encode = TokenEncodingModel(
        sub=username,
        exp=datetime.now(timezone.utc) + expires_delta,
        access_level=access_level,
        auth_type=TokenSourceModel.BEARER
    )
    # Return the encoded token
    return jwt.encode(
        to_encode.model_dump(), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
    )

def decode_jwt_token(token: str) -> TokenEncodingModel:
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
        )
        return TokenEncodingModel(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_bearer_token(authorization: str = Header(...)) -> str:
    if not authorization.lower().startswith(TokenSourceModel.BEARER):
        raise HTTPException(
            status_code=401, 
            detail="Invalid authorization header format"
        )
    return authorization.split(" ")[1]

# --- Authentication Methods ---
def authenticate_user(username: str, password: str) -> UserAuthenticationResponse:
    if verify_user(username, password):
        return UserAuthenticationResponse(
            username=username, auth_type=TokenSourceModel.LOGIN)
    return None

def firebase_token_authentication(
    firebase_token: str = Depends(get_bearer_token)
    ) -> UserAuthenticationResponse:
    try:
        decoded_token = auth.verify_id_token(firebase_token)
        return UserAuthenticationResponse(
            username=decoded_token["email"], 
            auth_type=TokenSourceModel.FIREBASE
        )
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Invalid Firebase token: {str(e)}")
        
async def get_current_user(
    request: Request, 
    authorization: Optional[str] = Security(api_key_header)
    ) -> UserAuthenticationResponse:
    # auth_header = request.headers.get("Authorization")
    if authorization:
        if authorization.lower().startswith(TokenSourceModel.LOGIN):
            logger.info("Basic auth header detected")
            return basic_authentication(authorization)
        else:
            logger.info("Bearer auth header detected")
            return bearer_authentication(authorization)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid credentials"
    )

def basic_authentication(auth_header: str) -> UserAuthenticationResponse:
    auth = auth_header.split(" ")[1]
    credentials = base64.b64decode(auth).decode("utf-8").split(":")
    username, password = credentials[0], credentials[1]
    if verify_user(username, password):
        return UserAuthenticationResponse(
            username=username, auth_type=TokenSourceModel.LOGIN)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Incorrect username or password"
    )

def bearer_authentication(authorization: str) -> UserAuthenticationResponse:
    """
    Authenticate using either a JWT token issued by our system or a Firebase token.

    If the token is a JWT issued by our system, the response will contain the username and authentication type will be "api_key". If the token is a Firebase token, the
    response will contain the username and authentication type will be "firebase".
    Args:
        authorization: The Authorization header containing the token
    Returns:
        A dictionary with keys "auth" and "user"
    Raises:
        HTTPException: If the token is invalid or of unknown type
    """
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != TokenSourceModel.BEARER:
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    logger.info(f"Authenticating using scheme: {scheme}")
    try:
        logger.info(f"Using JWT authentication")
        # Try to decode as a JWT token issued by our system
        token_info: TokenEncodingModel = decode_jwt_token(token)
        if token_info.auth_type == TokenSourceModel.BEARER:
            # JWT issued by our system
            username = token_info.sub
            if username is None:
                raise HTTPException(
                    status_code=401, detail="Invalid JWT token")
            return UserAuthenticationResponse(
                username=username, auth_type=TokenSourceModel.BEARER)
        else:
            raise HTTPException(
                status_code=401, detail="Unknown token type")
    except jwt.PyJWTError:
        # If decoding as JWT fails, attempt Firebase verification
        return firebase_token_authentication(token)

    
