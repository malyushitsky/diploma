from fastapi import APIRouter
from app.models.schemas import QARequest
from app.tasks.ask_task import ask_article_task

router = APIRouter()

@router.post("/")
def ask_async(req: QARequest):
    """
    Асинхронный запуск задачи на ответ на вопрос через Celery.
    """
    task = ask_article_task.delay(req.user_id, req.question)
    return {"message": "Задача на ответ пользователя по статье отправлена в очередь задач", "task_id": task.id}