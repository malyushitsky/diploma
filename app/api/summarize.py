from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.models.schemas import SummarizeRequest
from app.db.crud import get_user_arxiv_id, get_article_by_id
from app.db.database import get_db

router = APIRouter()


def trim_response(raw: str) -> str:
    """
    Обрезает генерацию модели после ключевых фраз или двойного переноса строки.

    args:
        raw (str): Сырой вывод LLM

    returns:
        str: Очищенный ответ
    """
    if "\n\n" in raw:
        raw = raw.split("\n\n")[0]

    cutoff_phrases = [
        "Вопрос:", "Теперь", "Также", "Ты прав", "Давай",
        "Рассмотрим", "Наконец"
    ]
    for phrase in cutoff_phrases:
        if phrase in raw:
            return raw.split(phrase)[0].strip()
    return raw.strip()


@router.post("/")
def summarize_article(request: Request, req: SummarizeRequest, db: Session = Depends(get_db)):
    """
    Генерирует краткое резюме статьи по её abstract и conclusion на основе user_id.

    args:
        request (Request): FastAPI request (для доступа к app.state.llm)
        req (SummarizeRequest): user_id пользователя
        db (Session): сессия БД через Depends
        
    returns:
        dict: arxiv_id, title, abstract, conclusion, summary
    """
    arxiv_id = get_user_arxiv_id(db, req.user_id)
    article = get_article_by_id(db, arxiv_id)

    if not article:
        return {"error": "Статья с таким ID не найдена."}

    full_text = f"Abstract:\n{article.abstract}\n\nConclusion:\n{article.conclusion}"
    prompt = f"Ты — помощник по научным статьям. Сформулируй краткое и точное резюме по тексту ниже.\n\n{full_text}\n\nКраткое резюме:"

    llm = request.app.state.llm
    response = llm(prompt, max_new_tokens=256, do_sample=False)[0]['generated_text']
    summary = response[len(prompt):].strip()
    summary = trim_response(summary)

    return {
        "arxiv_id": arxiv_id,
        "title": article.title,
        "summary": summary,
        "abstract": article.abstract,
        "conclusion": article.conclusion
    }