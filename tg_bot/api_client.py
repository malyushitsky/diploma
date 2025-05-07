import requests
from config import FASTAPI_URL

def ingest(user_id: str, url: str):
    res = requests.post(f"{FASTAPI_URL}/ingest", json={"user_id": user_id, "arxiv_url": url})
    return res.json()

def summarize(user_id: str):
    res = requests.post(f"{FASTAPI_URL}/summarize", json={"user_id": user_id})
    return res.json()

def ask(user_id: str, question: str):
    res = requests.post(f"{FASTAPI_URL}/question_answer", json={"user_id": user_id, "question": question})
    return res.json()

def ask_async(user_id: str, question: str):
    res = requests.post(f"{FASTAPI_URL}/ask_async", json={"user_id": user_id, "question": question})
    return res.json()

def summarize_async(user_id: str):
    res = requests.post(f"{FASTAPI_URL}/summarize_async", json={"user_id": user_id})
    return res.json()

def ingest_async(user_id: str, source: str, is_pdf: bool):
    res = requests.post(f"{FASTAPI_URL}/ingest_async", json={"user_id": user_id, "source": source, 'is_pdf': is_pdf})
    return res.json()

def get_task_result(task_id: str):
    res = requests.get(f"{FASTAPI_URL}/task_status/{task_id}")
    return res.json()