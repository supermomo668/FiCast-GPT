# Dev flow
# 1. Init sqplite db
# python -m app.models.session
# 2. start redis if not yet 
# . scripts/start-redis.sh
# 3. start celery
# . scripts/start-celery.sh
uvicorn app.main:app  --host 0.0.0.0 --port 42110 --reload
