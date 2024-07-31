#!/bin/bash

# start the api server
uvicorn server.router.main:app --host 0.0.0.0 --port 8000 --reload