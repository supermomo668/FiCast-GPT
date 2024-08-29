import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from apps.api.app.main import app
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(".env")

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_hydra_compose():
    with patch('ficast.config.compose') as mock_compose:
        mock_compose.return_value = {}
        yield
        
client = TestClient(app)

@pytest.fixture
def test_user():
    return {
        "username": os.getenv("DEFAULT_USERNAME", "testuser"),
        "password": os.getenv("DEFAULT_PASSWORD", "testpassword")
    }

def test_login_success(test_user):
    response = client.post("/auth/login", data=test_user)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"

def test_login_failure():
    response = client.post("/auth/login", data={"username": "wrong", "password": "wrong"})
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert response.json()["detail"] == "Incorrect username or password"

@pytest.fixture
def auth_headers(test_user):
    response = client.post("/auth/login", data=test_user)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return headers

def test_verify_token_success(auth_headers):
    response = client.get(
        "/auth/verify-token", headers=auth_headers)
    assert response.status_code == 200
    json_response = response.json()
    assert "status" in json_response and json_response["status"] == "success"

def test_verify_token_failure():
    headers = {
        "Authorization": "Bearer invalidtoken"
    }
    response = client.get("/auth/verify-token", headers=headers)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"