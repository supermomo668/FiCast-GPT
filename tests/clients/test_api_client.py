import os
import dotenv
import logging
import time
from elevenlabs import Voice
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
        base_url=os.getenv("TTS_API_BASE_URL"),
        api_key=os.getenv("TTS_API_KEY")
    )

@pytest.fixture(scope="module")
def shared_state():
    return {}

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
    assert len(voices_by_id) >= 1, "There should be voices"
    assert all(
        isinstance(k, str) and isinstance(v, Voice) for k, v in voices_by_id.items()), "all keys and values must be int and str"
    logger.info("Completed test_get_all_voices_by_id successfully")

def test_task_creation(api_client, shared_state):
    # Submit a text-to-speech task
    response = api_client.client.post(
        f"{api_client.base_url}/tts",
        json={
            "text": "Hello, Test!",
            "voice": os.getenv("TTS_API_VOICE_NAME"),
            "preset": "ultra_fast"
        }, 
        headers={
            "Authorization": f"Bearer {os.getenv('TTS_API_KEY')}"
        }
    )
    response.raise_for_status()
    task_id = response.json().get("task_id")
    assert task_id is not None

    # Store the task_id in shared state
    shared_state['task_id'] = task_id
    print(f"Shared task created: {task_id}")
    # Check that the task is in the queue
    response = api_client.client.get(
        f"{api_client.base_url}/queue-status"
    )
    response.raise_for_status()
    queue_status = response.json()
    assert task_id in queue_status["tasks"]
    assert queue_status["tasks"][task_id]["status"] in ["queued", "in_progress"]

def test_task_completion(api_client, shared_state):
    task_id = shared_state.get('task_id')
    assert task_id is not None, "Task ID not found in shared state. Ensure that test_task_creation runs before test_task_completion."

    # Wait for the task to complete
    start_time = time.time()
    while True:
        response = api_client.client.get(
            f"{api_client.base_url}/task-status/{task_id}"
        )
        response.raise_for_status()
        task_status = response.json()
        if task_status["status"] == "completed":
            break
        elif task_status["status"] == "failed":
            raise AssertionError(
                "Task failed: "+ response.text)
        elif time.time() - start_time > 60:
            raise AssertionError(
                "Task did not complete within 1 minute: "+ response.text)
        time.sleep(5)

    # Verify that the task is completed
    assert task_status["status"] == "completed"
    assert task_status["result"] is not None

def test_queue_status_api_key(api_client):
    response = api_client.client.get(
        "/queue-status",
        headers={
            "Authorization": f"Bearer {os.getenv('TTS_API_KEY')}"
        }
    )
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    assert 'tasks' in response.json(), f"'tasks' key missing in response. Response: {response.json()}"