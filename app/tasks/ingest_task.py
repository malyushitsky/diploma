from fastapi import APIRouter
from app.db.database import SessionLocal
from app.services.article_parser import parse_and_split_article, extract_arxiv_id
from app.services.vectorstore import store_chunks
from app.celery_globals import embedding_model
from celery_app import celery
from app.db.crud import (
    get_article_by_id,
    save_article_metadata,
    get_user_arxiv_id,
    register_user_session
)

router = APIRouter()

@celery.task
def ingest_article_task(user_id: str, arxiv_url: str):
    """
    Фоновая задача: загружает и обрабатывает статью с arXiv,
    сохраняет чанки в ChromaDB, метаданные в БД и привязывает к пользователю.

    args:
        user_id (str): Telegram user ID
        arxiv_url (str): ссылка на статью
    returns:
        dict: результат обработки
    """
    db = SessionLocal()

    try:
        arxiv_id = extract_arxiv_id(arxiv_url)
        
        if get_article_by_id(db, arxiv_id):
            register_user_session(db, user_id, arxiv_id)
            return {
                "message": "Статья уже есть в БД, сессия пользователя обновлена",
                "arxiv_id": arxiv_id,
                "skipped": True
            }
    
        arxiv_id, title, md_cleaned, abstract, conclusion = parse_and_split_article(arxiv_url)
    
        chunks = store_chunks(md_cleaned, arxiv_id, title, embedding_model)
    
        # Сохраняем метаданные и сессию
        save_article_metadata(db, arxiv_id, title, abstract, conclusion)
        register_user_session(db, user_id, arxiv_id)
    
        return {
            "message": "Статья обработана успешно",
            "arxiv_id": arxiv_id,
            "title": title,
            "num_chunks": len(chunks)
        }
        
    finally:
        db.close()
