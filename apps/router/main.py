from fastapi import FastAPI, HTTPException, APIRouter, Header
from fastapi.middleware.cors import CORSMiddleware

import firebase_admin
from firebase_admin import credentials, auth
import os
from fastapi import FastAPI, APIRouter
from dotenv import dotenv_values

config = dotenv_values(".env")


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize Firebase Admin SDK
# TODO: create config yaml file with pydantic validators
#       for all the nec. inputs
#       no need to rely on env vars
print(config)
path = os.path.abspath(config.get("GCLOUD_PROJECT_CONFIG_JSON_PATH"))
cred = credentials.Certificate(path)
firebase_admin.initialize_app(cred)


app = FastAPI()

router = APIRouter()


@router.get("/version")
async def root():
    return {"message": "Hello World from v1"}


app.include_router(router, prefix="/v1")

# Import and include the auth router
# Import here so that firebase is already initialized
# TODO: make config and initializers for Fastapi, so firebase is
#  initialized before reaching here
from .auth import router as auth_router

app.include_router(auth_router, prefix="/v1/auth")
