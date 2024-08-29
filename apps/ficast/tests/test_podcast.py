import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.db import init_db, get_db, TaskModel, PodcastModel, SessionLocal
from app.tasks import Task
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(".test.env")

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def auth_headers():
    test_user = {
        "username": os.getenv("DEFAULT_USERNAME"),
        "password": os.getenv("DEFAULT_PASSWORD")
    }
    response = client.post("/auth/login", data=test_user)
    token = response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return headers

@pytest.fixture
def podcast_request_payload():
    return {
        "topic": "Test Topic",
        "n_rounds": 5,
        "participants": [
            {
                "name": "Test Host",
                "description": "Test Host Description",
                "model": "gpt-3.5-turbo",
                "role": "host"
            },
            {
                "name": "Test Guest",
                "description": "Test Guest Description",
                "model": "gpt-3.5-turbo"
            }
        ]
    }

def test_create_podcast(db: Session, auth_headers, podcast_request_payload):
    # Test creating a podcast
    response = client.post("/podcast/create", json=podcast_request_payload, headers=auth_headers)
    assert response.status_code == 200
    task_id = response.json()
    assert task_id is not None

    # Verify task is saved in the database
    task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
    assert task is not None
    assert task.status == "pending" or task.status == "completed"

def test_get_podcast_script(db: Session, auth_headers):
    # Create a podcast and wait for the task to complete (for non-Celery mode)
    task_id = test_create_podcast(db, auth_headers, podcast_request_payload={})
    
    # Test retrieving the podcast script
    response = client.get(f"/podcast/{task_id}/script", headers=auth_headers)
    assert response.status_code == 200
    script = response.json()
    assert "dialogues" in script
    assert len(script["dialogues"]) > 0

def test_generate_podcast_audio(db: Session, auth_headers):
    # Create a podcast
    task_id = test_create_podcast(db, auth_headers, podcast_request_payload={})
    
    # Test creating audio generation task
    response = client.post(f"/podcast/{task_id}/audio", headers=auth_headers)
    assert response.status_code == 200
    audio_id = response.json()
    assert audio_id is not None

    # Verify audio task is saved in the database
    audio_task = db.query(TaskModel).filter(TaskModel.task_id == audio_id).first()
    assert audio_task is not None
    assert audio_task.status == "pending" or audio_task.status == "completed"

def test_get_podcast_audio(db: Session, auth_headers):
    # Create a podcast and generate audio
    task_id = test_create_podcast(db, auth_headers, podcast_request_payload={})
    audio_id = test_generate_podcast_audio(db, auth_headers)

    # Test retrieving the podcast audio
    response = client.get(f"/podcast/{task_id}/{audio_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert response.content is not None
