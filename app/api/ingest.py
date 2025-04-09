from fastapi import APIRouter, Query, Request
from app.services.article_parser import parse_and_split_article, extract_arxiv_id
from app.services.vectorstore import store_chunks
from app.services.metadata_store import update_metadata, load_metadata

router = APIRouter()


# @router.post("/")
# def ingest_article(request: Request, url: str = Query(..., description="arXiv article URL")):
#     """
#     Загружает и обрабатывает статью с arXiv, сохраняет чанки в ChromaDB и обновляет кэш метаданных.

#     args:
#         request (Request): Объект запроса (для доступа к app.state.embedding_model)
#         url (str): Ссылка на статью arXiv (https://arxiv.org/abs/...)

#     returns:
#         dict: Сообщение об успешной загрузке, arxiv_id и количество чанков
#     """
#     arxiv_id = extract_arxiv_id(url)

#     if arxiv_id in load_metadata():
#         return {
#             "message": "Статья уже есть в БД",
#             "arxiv_id": arxiv_id,
#             "skipped": True
#         }

#     arxiv_id, title, md_cleaned, abstract, conclusion = parse_and_split_article(url)
#     embedding_model = request.app.state.embedding_model
#     chunks = store_chunks(md_cleaned, arxiv_id, title, embedding_model)
#     update_metadata(arxiv_id, title, abstract, conclusion)

#     return {
#         "message": "Статья обработана успешно",
#         "arxiv_id": arxiv_id,
#         "title": title,
#         "num_chunks": len(chunks)
#     }

from fastapi import APIRouter, Request, Query
from app.models.schemas import IngestRequest
from app.services.article_parser import parse_and_split_article, extract_arxiv_id
from app.services.metadata_store import save_metadata, load_metadata
from app.services.vectorstore import store_chunks
from app.services.user_sessions import register_user_session

router = APIRouter()

@router.post("/")
def ingest_article(request: Request, req: IngestRequest):
    """
    Загружает и обрабатывает статью с arXiv, сохраняет чанки в ChromaDB, обновляет кэш метаданных,
    и регистрирует пользователя, загрузившего статью.

    args:
        request (Request): Объект запроса (для доступа к app.state.embedding_model)
        req (IngestRequest): user_id и arxiv_url

    returns:
        dict: Информация об обработке статьи
    """
    arxiv_id = extract_arxiv_id(req.arxiv_url)

    if arxiv_id in load_metadata():
        register_user_session(req.user_id, arxiv_id)
        return {
            "message": "Статья уже есть в БД, сессия пользователя обновлена",
            "arxiv_id": arxiv_id,
            "skipped": True
        }

    arxiv_id, title, md_cleaned, abstract, conclusion = parse_and_split_article(req.arxiv_url)
    embedding_model = request.app.state.embedding_model
    chunks = store_chunks(md_cleaned, arxiv_id, title, embedding_model)
    update_metadata(arxiv_id, title, abstract, conclusion)
    register_user_session(req.user_id, arxiv_id)

    return {
        "message": "Статья обработана успешно",
        "arxiv_id": arxiv_id,
        "title": title,
        "num_chunks": len(chunks)
    }






