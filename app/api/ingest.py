from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.models.schemas import IngestRequest
from app.services.article_parser import parse_and_split_article, extract_arxiv_id
from app.services.vectorstore import store_chunks
from app.db.database import get_db
from app.db.crud import (
    get_article_by_id,
    save_article_metadata,
    get_user_arxiv_id,
    register_user_session
)

router = APIRouter()

@router.post("/")
def ingest_article(request: Request, req: IngestRequest, db: Session = Depends(get_db)):
    """
    Загружает и обрабатывает статью с arXiv, сохраняет чанки в ChromaDB,
    сохраняет метаданные в БД и регистрирует сессию пользователя.

    args:
        request (Request): FastAPI request (с доступом к embedding_model)
        req (IngestRequest): user_id и arxiv_url
        db (Session): сессия БД через Depends

    returns:
        dict: Информация об обработке статьи
    """
    arxiv_id = extract_arxiv_id(req.arxiv_url)
    
    if get_article_by_id(db, arxiv_id):
        register_user_session(db, req.user_id, arxiv_id)
        return {
            "message": "Статья уже есть в БД, сессия пользователя обновлена",
            "arxiv_id": arxiv_id,
            "skipped": True
        }

    arxiv_id, title, md_cleaned, abstract, conclusion = parse_and_split_article(req.arxiv_url)

    embedding_model = request.app.state.embedding_model
    chunks = store_chunks(md_cleaned, arxiv_id, title, embedding_model)

    # Сохраняем метаданные и сессию
    save_article_metadata(db, arxiv_id, title, abstract, conclusion)
    register_user_session(db, req.user_id, arxiv_id)

    return {
        "message": "Статья обработана успешно",
        "arxiv_id": arxiv_id,
        "title": title,
        "num_chunks": len(chunks)
    }
