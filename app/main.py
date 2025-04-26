from fastapi import FastAPI
from app.api import summarize_async, ingest_async, ask_async, task_status

app = FastAPI(title="arXiv RAG API")

app.include_router(summarize_async.router, prefix="/summarize_async", tags=["Summarize_async"])
app.include_router(ingest_async.router, prefix="/ingest_async", tags=["Ingest_async"])
app.include_router(ask_async.router, prefix="/ask_async", tags=["Ask_async"])
app.include_router(task_status.router, prefix="/task_status/{task_id}", tags=["Task_status"])

@app.get("/")
def root():
    return {"message": "arXiv RAG API"}