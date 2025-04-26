from fastapi import APIRouter
from app.models.schemas import IngestRequest
from app.tasks.ingest_task import ingest_article_task

router = APIRouter()

@router.post("/")
def ingest_async(req: IngestRequest):
    task = ingest_article_task.delay(req.user_id, req.arxiv_url)
    return {"message": "Задача парсинга и загрузки метаданных в БД отправлена в очередь задач", "task_id": task.id}