#!/bin/bash
# # Activate the Poetry environment
source $(poetry env info --path)/bin/activate

# # Debug: Print the path to check if the environment is activated
echo "Poetry environment path: $(poetry env info --path)"

# Execute the Python script with passed arguments
USE_CELERY=1 uvicorn app.main:app "$@"