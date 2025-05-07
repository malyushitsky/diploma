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
def ingest_article_task(user_id: str, source: str, is_pdf: bool = False) -> dict:
    """
    Загружает и обрабатывает статью (по ссылке или PDF).

    Args:
        user_id (str): Telegram user_id
        source (str): либо arXiv-ссылка, либо путь к PDF
        is_pdf (bool): True, если это PDF-файл, False — если ссылка
    """
    db = SessionLocal()

    try:
        arxiv_id, title, md_cleaned, abstract, conclusion = parse_and_split_article(source, is_pdf)

        if get_article_by_id(db, arxiv_id):
            register_user_session(db, user_id, arxiv_id)
            return {
                "message": f"Статья уже загружена ранее. Привязана к вашему профилю.",
                "arxiv_id": arxiv_id,
                "skipped": True
            }

        chunks = store_chunks(md_cleaned, arxiv_id, title, embedding_model)
        save_article_metadata(db, arxiv_id, title, abstract, conclusion)
        register_user_session(db, user_id, arxiv_id)

        return {
            "message": f"Статья '{title}' обработана успешно",
            "arxiv_id": arxiv_id,
            "title": title,
            "num_chunks": len(chunks)
        }

    finally:
        db.close()
