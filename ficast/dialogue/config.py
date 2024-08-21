import httpx
from tenacity import stop_never


MAX_RETRY = 25  # not used 
MAX_DELAY = stop_never
WAIT_BETWEEN_RETRY = 6
CLIENT_TIMEOUT = httpx.Timeout(None)