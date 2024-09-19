APP_ROOT="/api"
API_DOC = "/v1/docs"
API_REDOC = "/v1/redoc"
PRIVACY_POLICY_PATH = "app/data/privacy_policy.html"

import os

USE_CELERY = os.getenv("USE_CELERY").lower() in ("true", "1")