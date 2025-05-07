from pydantic import BaseModel


class IngestRequest(BaseModel):
    user_id: str
    source:str
    is_pdf: bool

class QARequest(BaseModel):
    user_id: str
    question: str


class SummarizeRequest(BaseModel):
    user_id: str