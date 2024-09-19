#!/bin/bash
celery -A app.tasks.task "$@"