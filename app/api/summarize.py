from fastapi import APIRouter, Query, Request
from app.services.metadata_store import load_metadata

router = APIRouter()

def trim_response(raw: str) -> str:
    """
    Обрезаем вывод модели
    
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

# @router.post("/summarize")
# def summarize_article(request: Request, arxiv_id: str = Query(..., description="arXiv ID статьи для суммаризации")):
#     """
#     Возвращает краткое содержание статьи на основе abstract и conclusion, сгенерированное через LLM.

#     args:
#         request (Request): FastAPI request (для доступа к app.state.llm)
#         arxiv_id (str): ID статьи в arXiv (например, '2501.08248')

#     returns:
#         dict: Структурированный ответ с summary, abstract, conclusion
#     """
#     metadata = load_metadata()
#     article = metadata.get(arxiv_id)

#     if not article:
#         return {"error": "Статья с таким ID не найдена."}

#     abstract = article.get("abstract", "")
#     conclusion = article.get("conclusion", "")

#     llm = request.app.state.llm

#     full_text = f"Abstract:\n{abstract}\n\nConclusion:\n{conclusion}"
#     prompt = f"Ты — помощник по научным статьям. Сформулируй краткое и точное резюме по тексту ниже.\n\n{full_text}\n\nКраткое резюме:"  

#     response = llm(prompt, max_new_tokens=300, do_sample=False)[0]['generated_text']
#     summary = response[len(prompt):].strip()
#     summary = trim_response(summary)

#     return {
#         "arxiv_id": arxiv_id,
#         "title": article.get("title"),
#         "summary": summary,
#         "abstract": abstract,
#         "conclusion": conclusion
#     }

from fastapi import APIRouter, Request
from app.models.schemas import SummarizeRequest
from app.services.metadata_store import load_metadata
from app.services.user_sessions import get_user_article

router = APIRouter()

def trim_response(raw: str) -> str:
    """
    Обрезает генерацию модели после ключевых фраз или двойного переноса строки.

    args:
        raw (str): Сырый вывод LLM

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
def summarize_article(request: Request, req: SummarizeRequest):
    """
    Генерирует краткое резюме статьи по её abstract и conclusion на основе user_id.

    args:
        request (Request): FastAPI request (для доступа к app.state.llm)
        req (SummarizeRequest): user_id пользователя

    returns:
        dict: arxiv_id, title, abstract, conclusion, summary
    """
    arxiv_id = get_user_article(req.user_id)
    metadata = load_metadata()
    article = metadata.get(arxiv_id)

    if not article:
        return {"error": "Статья с таким ID не найдена."}

    abstract = article.get("abstract", "")
    conclusion = article.get("conclusion", "")
    full_text = f"Abstract:\n{abstract}\n\nConclusion:\n{conclusion}"
    prompt = f"Ты — помощник по научным статьям. Сформулируй краткое и точное резюме по тексту ниже.\n\n{full_text}\n\nКраткое резюме:"

    llm = request.app.state.llm

    response = llm(prompt, max_new_tokens=256, do_sample=False)[0]['generated_text']
    summary = response[len(prompt):].strip()
    summary = trim_response(summary)

    return {
        "arxiv_id": arxiv_id,
        "title": article.get("title"),
        "summary": summary,
        "abstract": abstract,
        "conclusion": conclusion
    }