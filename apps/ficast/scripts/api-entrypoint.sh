#!/bin/bash
# # Activate the Poetry environment
# source $(poetry env info --path)/bin/activate

# # Debug: Print the path to check if the environment is activated
# echo "Poetry environment path: $(poetry env info --path)"

# Debug: Check if uvicorn is available
uvicorn_path=$(which uvicorn)
echo "Uvicorn path: $uvicorn_path"
# Execute the Python script with passed arguments
uvicorn app.main:app "$@"