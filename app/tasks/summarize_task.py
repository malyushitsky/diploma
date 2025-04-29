from typing import List
from celery_app import celery
from app.db.database import SessionLocal
from app.db.crud import get_user_arxiv_id, get_article_by_id
from app.celery_globals import llm, terminators

SYSTEM_MSG = (
    "Ты — помощник по научным статьям. "
    "Сформулируй краткое и точное резюме по тексту ниже."
)

def build_messages(article) -> list[dict]:
    full_text = f"Abstract:\n{article.abstract}\n\nConclusion:\n{article.conclusion}"

    return [
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user", "content": full_text},
        {"role": "assistant", "content": "Краткое резюме:"},
    ]


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

        # Формируем prompt
        full_text = f"Abstract:\n{article.abstract}\n\nConclusion:\n{article.conclusion}"
        prompt = f"""Ты — помощник по научным статьям. Сформулируй краткое и точное резюме по тексту ниже.\n\n{full_text}\n\nКраткое резюме:"""

        messages = build_messages(article)
        summary = llm(messages, max_new_tokens=256, do_sample=False, eos_token_id=terminators)[0]['generated_text']

        # Возвращаем данные
        return {
            "arxiv_id": arxiv_id,
            "title": article.title,
            "summary": summary,
            "abstract": article.abstract,
            "conclusion": article.conclusion
        }

    finally:
        db.close()
