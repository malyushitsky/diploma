from celery.result import AsyncResult
from celery_app import celery
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery)

    if task_result.ready():
        if task_result.successful():
            return {"status": "completed", "result": task_result.result}
        else:
            return {"status": "failed", "error": str(task_result.result)}
    else:
        return {"status": "pending"}