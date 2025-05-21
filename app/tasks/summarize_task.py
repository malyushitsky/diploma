from typing import List
from celery_app import celery
from app.db.database import SessionLocal
from app.db.crud import get_user_arxiv_id, get_article_by_id
from app.celery_globals import llm, tokenizer
import redis
import hashlib
import json

SYSTEM_MSG = (
    "Ты — помощник по научным статьям. "
    "Сформулируй краткое и точное резюме по тексту ниже. Отвечай строго на русском языке"
)

def build_messages(article) -> list[dict]:
    full_text = f"Abstract:\n{article.abstract}\n\nConclusion:\n{article.conclusion}"

    return [
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user", "content": full_text},
        {"role": "assistant", "content": "Краткое резюме:"},
    ]

def make_cache_key(arxiv_id: str) -> str:
    return f"summary:{arxiv_id}"

@celery.task
def summarize_article_task(user_id: str) -> dict:
    """
    Фоновая задача: генерирует краткое резюме статьи, связанной с user_id.

    args:
        user_id (str): id пользователя
    """

    db = SessionLocal()

    try:
        # Получаем arxiv_id пользователя
        arxiv_id = get_user_arxiv_id(db, user_id)
        if not arxiv_id:
            return {"error": "У пользователя нет связанной статьи"}
        
        # Получаем метаданные статьи из базы данных
        article = get_article_by_id(db, arxiv_id)
        if not article:
            return {"error": "Статья не найдена"}

        # Проверка кеша
        cache_key = make_cache_key(arxiv_id)
        cached = r.get(cache_key)
        if cached:
            return json.loads(cached)
            
        # Используем chat_template
        messages = build_messages(article)
        messages = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        summary = llm(messages, max_new_tokens=256, temperature=0.7, top_p=0.8, top_k=20, min_p=0)[0]['generated_text']

        result = {
            "arxiv_id": arxiv_id,
            "title": article.title,
            "summary": summary,
            "abstract": article.abstract,
            "conclusion": article.conclusion
        }
        
        # Сохранение кеша на 24ч
        r.set(cache_key, json.dumps(result, ensure_ascii=False), ex=60 * 60 * 24) 
        return result

    finally:
        db.close()
