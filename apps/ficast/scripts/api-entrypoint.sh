#!/bin/bash

# Execute the Python script with passed arguments
uvicorn app.main:app "$@"