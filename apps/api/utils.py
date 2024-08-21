import os
import base64
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from celery import Celery
from fastapi import Security, HTTPException, Request, status
from fastapi.security import HTTPBasic, APIKeyHeader
from jose import jwt

# Load environment variables
DEFAULT_SECRET_KEY = str(os.getenv("DEFAULT_SECRET_KEY", "fek3kz9xzlsndSuczhgjds0vndi"))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 24*60))

# Security objects for Basic Auth and API Key
security = HTTPBasic()
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def create_celery(app):
    # Create and configure Celery app
    celery_app = Celery('api')
    # Load configuration from environment variables
    celery_app.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    celery_app.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    celery_app.conf.task_serializer = os.getenv('CELERY_TASK_SERIALIZER', 'json')
    celery_app.conf.result_serializer = os.getenv('CELERY_RESULT_SERIALIZER', 'json')
    celery_app.conf.accept_content = os.getenv('CELERY_ACCEPT_CONTENT', 'json').split(',')
    celery_app.conf.timezone = os.getenv('CELERY_TIMEZONE', 'UTC')
    celery_app.conf.enable_utc = os.getenv('CELERY_ENABLE_UTC', 'True').lower() == 'true'
    celery_app.conf.worker_concurrency = int(os.getenv('CELERY_WORKER_CONCURRENCY', '1'))
    celery_app.conf.worker_prefetch_multiplier = int(os.getenv('CELERY_PREFETCH_MULTIPLIER', '1'))
    return celery_app

def verify_user(username: str, password: str) -> bool:
    correct_username = secrets.compare_digest(username, os.getenv("DEFAULT_USERNAME"))
    correct_password = secrets.compare_digest(password, os.getenv("DEFAULT_PASSWORD"))
    return correct_username and correct_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, DEFAULT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    request: Request,  
    authorization: Optional[str] = Security(api_key_header)
):
    auth_header = request.headers.get("Authorization")
    
    # Basic Authentication
    if auth_header and auth_header.startswith("Basic "):
        auth = auth_header.split(" ")[1]
        credentials = base64.b64decode(auth).decode("utf-8").split(":")
        username = credentials[0]
        password = credentials[1]
        
        if verify_user(username, password):
            return {"auth": "basic", "user": username}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )

    # JWT Authentication
    elif authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401, detail="Invalid authentication scheme"
            )
        
        try:
            payload = jwt.decode(token, DEFAULT_SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Could not validate credentials")
            return {"auth": "api_key", "user": username}
        
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
