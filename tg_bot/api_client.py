import requests
from config import FASTAPI_URL

def ingest_article(user_id: str, url: str):
    res = requests.post(f"{FASTAPI_URL}/ingest", json={"user_id": user_id, "arxiv_url": url})
    return res.json()

def summarize(user_id: str):
    res = requests.post(f"{FASTAPI_URL}/summarize", json={"user_id": user_id})
    return res.json()

def ask(user_id: str, question: str):
    res = requests.post(f"{FASTAPI_URL}/question_answer", json={"user_id": user_id, "question": question})
    return res.json()