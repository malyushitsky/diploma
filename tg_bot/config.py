import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Local FASTAPI_URL = "http://localhost:8000"
FASTAPI_URL = "http://fastapi_app:8000"