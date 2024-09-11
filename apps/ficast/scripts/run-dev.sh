# manually initiate database
# python -m app.models.session
# start redis if not yet 
# docker run -d --name celery-redis -p 6379:6379 redis
# start celery
# HYDRA_CONFIG_NAME=api USE_CELERY=1 celery -A app.tasks.task.celery_app worker --loglevel=info
uvicorn app.main:app  --host 0.0.0.0 --port 42110 --reload
