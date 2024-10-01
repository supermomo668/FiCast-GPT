#!/bin/bash
# # Activate the Poetry environment
source $(poetry env info --path)/bin/activate

# # Debug: Print the path to check if the environment is activated
echo "Poetry environment path: $(poetry env info --path)"


# start celery worker
USE_CELERY=1 celery -A app.tasks.task.celery_app "$@"
            celery -A app.tasks.task.celery_app worker --loglevel=info