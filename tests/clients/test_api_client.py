import os
import dotenv
import logging
import time
from typing import Generator
import pytest

from ficast.dialogue.clients import APIClient

# Load environment variables
load_env = dotenv.load_dotenv("tests/.env")
assert load_env

# Configure logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.fixture
def api_client():
    assert os.getenv("TTS_API_BASE_URL")
    return APIClient(
        base_url=os.getenv("TTS_API_BASE_URL"))

def test_get_all_voices(api_client):
    logger.info("Starting test_get_all_voices")
    voices = api_client.all_voices
    logger.info(f"Voices received: {voices}")
    
    assert isinstance(voices, list)
    assert len(voices) > 0
    logger.info("Completed test_get_all_voices successfully")

def test_get_all_voices_by_id(api_client):
    logger.info("Starting test_get_all_voices_by_id")
    voices_by_id = api_client.all_voices_by_id
    logger.info(f"Voices by ID received: {voices_by_id}")
    assert isinstance(voices_by_id, dict)
    assert all(
        isinstance(k, int) and isinstance(v, str) for k, v in voices_by_id.items()), "all keys and values must be int and str"
    logger.info("Completed test_get_all_voices_by_id successfully")

def test_task_creation(api_client):
    # Submit a text-to-speech task
    response = api_client.client.post(
        f"{api_client.base_url}/tts",
        json={
            "text": "Hello, Test!",
            "voice": os.getenv("TTS_API_VOICE_NAME"),
            "preset": "ultra_fast"
        },
        auth=(os.getenv("TTS_API_USERNAME"), os.getenv("TTS_API_PASSWORD"))
    )
    response.raise_for_status()
    task_id = response.json().get("task_id")
    assert task_id is not None

    # Check that the task is in the queue
    response = api_client.client.get(
        f"{api_client.base_url}/queue-status",
        auth=(os.getenv("TTS_API_USERNAME"), os.getenv("TTS_API_PASSWORD"))
    )
    response.raise_for_status()
    queue_status = response.json()
    assert task_id in queue_status["tasks"]
    assert queue_status["tasks"][task_id]["status"] in ["queued", "in_progress"]

def test_task_completion(api_client):
    # Submit a text-to-speech task
    response = api_client.client.post(
        f"{api_client.base_url}/tts",
        json={
            "text": "Hello, Test!",
            "voice": os.getenv("TTS_API_VOICE_NAME"),
            "preset": "ultra_fast"
        },
        auth=(os.getenv("TTS_API_USERNAME"), os.getenv("TTS_API_PASSWORD"))
    )
    response.raise_for_status()
    task_id = response.json().get("task_id")
    assert task_id is not None

    # Wait for the task to complete
    start_time = time.time()
    while True:
        response = api_client.client.get(
            f"{api_client.base_url}/task-status/{task_id}",
            auth=(os.getenv("TTS_API_USERNAME"), os.getenv("TTS_API_PASSWORD"))
        )
        response.raise_for_status()
        task_status = response.json()
        if task_status["status"] == "completed":
            break
        elif task_status["status"] == "failed":
            raise AssertionError("Task failed")
        elif time.time() - start_time > 60:
            raise AssertionError("Task did not complete within 1 minute")
        time.sleep(5)

    # Verify that the task is completed
    assert task_status["status"] == "completed"
    assert task_status["result"] is not None