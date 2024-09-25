#!/bin/bash
export PYTHONPATH="$PWD/../.."  # require local `ficast` module in the path
HYDRA_CONFIG_NAME=api USE_CELERY=1 celery -A app.tasks.task.celery_app worker --loglevel=info