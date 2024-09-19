
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

def load_env_credentials() -> Dict[str, str]:
    env_username = os.getenv("DEFAULT_USERNAME")
    env_password = os.getenv("DEFAULT_PASSWORD")
    assert env_username and env_password, "DEFAULT_USERNAME and DEFAULT_PASSWORD environment variables must be set"
    return {"username": env_username, "password": env_password}