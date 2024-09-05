import os
import base64
import secrets
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

from fastapi import Depends, Header, Security, HTTPException, Request, status
from fastapi.security import HTTPBasic, APIKeyHeader

from firebase_admin import credentials, auth
import firebase_admin

from ..logger import logger
from ..utils import load_env_credentials

# Load environment variables
from dotenv import load_dotenv
load_dotenv(".env")

# Load environment variables
JWT_SECRET_KEY = str(os.getenv("JWT_SECRET_KEY"))
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60*24*7))
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

assert FIREBASE_CREDENTIALS_PATH, "FIREBASE_CREDENTIALS_PATH environment variable must be set"

# Initialize Firebase Admin SDK
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

# Security objects for Basic Auth and API Key
security = HTTPBasic()
api_key_header = APIKeyHeader(
  name="Authorization", auto_error=False)

def verify_user(username: str, password: str) -> bool:
    creds = load_env_credentials()
    correct_username = secrets.compare_digest(username, creds["username"])
    correct_password = secrets.compare_digest(password, creds["password"])
    return correct_username and correct_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update(
      {"exp": expire, "auth_type": "internal"})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    return jwt.decode(
      token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
  
# --- Authentication Methods ---

def authenticate_user(username: str, password: str) -> Optional[Dict[str, str]]:
    if verify_user(username, password):
        return {"username": username}
    return None

async def get_current_user(request: Request, authorization: Optional[str] = Security(api_key_header)) -> dict:
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Basic "):
        return basic_authentication(auth_header)
    
    if authorization:
        return bearer_authentication(authorization)

    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalidcredentials")

def basic_authentication(auth_header: str) -> dict:
    auth = auth_header.split(" ")[1]
    credentials = base64.b64decode(auth).decode("utf-8").split(":")
    username, password = credentials[0], credentials[1]
    if verify_user(username, password):
        return {"auth": "basic", "user": username}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

def bearer_authentication(authorization: str) -> dict:
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
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    logger.info(f"Authenticating using scheme: {scheme}")
    try:
        logger.info(f"Using JWT authentication")
        # Try to decode as a JWT token issued by our system
        payload = decode_jwt_token(token)
        if payload.get("auth_type") == "internal":
            # JWT issued by our system
            username = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid JWT token")
            return {"auth": "api_key", "user": username}
        else:
            raise HTTPException(status_code=401, detail="Unknown token type")
    except jwt.PyJWTError:
        # If decoding as JWT fails, attempt Firebase verification
        return firebase_authentication(token)

def get_bearer_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    return authorization.split(" ")[1]
  
def firebase_authentication(firebase_token: str = Depends(get_bearer_token)) -> dict:
    try:
        decoded_token = auth.verify_id_token(firebase_token)
        return {"auth": "firebase", "user": decoded_token["email"]}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {str(e)}")
    
