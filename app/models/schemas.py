from pydantic import BaseModel


class IngestRequest(BaseModel):
    user_id: str
    arxiv_url: str


class QARequest(BaseModel):
    user_id: str
    question: str


class SummarizeRequest(BaseModel):
    user_id: str