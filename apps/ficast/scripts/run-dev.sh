#!/bin/bash
export PYTHONPATH="$PWD/../.."  # require local `ficast` module in the path

# Dev flow
# 1. Init sqplite db
# python -m app.models.session
# 2. start redis if not yet 
# . scripts/redis-run-dev.sh
# 3. start celery
# . scripts/celery-run-dev.sh
HYDRA_CONFIG_NAME=api HYDRA_CONFIG_PATH="../conf/dialogue" uvicorn app.main:app  --host 0.0.0.0 --port 42110 --reload
