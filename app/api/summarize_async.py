from fastapi import APIRouter
from app.models.schemas import SummarizeRequest
from app.tasks.summarize_task import summarize_article_task

router = APIRouter()

@router.post("/")
def summarize_async(req: SummarizeRequest):
    task = summarize_article_task.delay(req.user_id)
    return {"message": "Задача суммаризации отправлена в очередь задач", "task_id": task.id}