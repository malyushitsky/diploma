from fastapi import APIRouter, Request
from app.models.schemas import QARequest
from app.services.user_sessions import get_user_article
from app.services.vectorstore import retrieve_and_rerank

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


@router.post("/")
def question_answer(request: Request, req: QARequest):
    """
    Задаёт вопрос по статье, привязанной к Telegram-пользователю. Требует, чтобы ранее была вызвана /ingest.

    args:
        request (Request): FastAPI Request с доступом к векторной БД
        req (QARequest): запрос с user_id и вопросом

    returns:
        dict: ответ, релевантные документы, найденный arxiv_id
    """
    user_id = req.user_id
    question = req.question

    arxiv_id = get_user_article(user_id)
    if not arxiv_id:
        return {"error": "Для этого пользователя ещё не была загружена статья. Сначала вызовите /ingest."}

    vectordb = request.app.state.vectorstore
    reranker = request.app.state.reranker
    
    # Поиск и ранжирование релевантных документов
    reranked = retrieve_and_rerank(question, vectordb, reranker, arxiv_id, top_k=10, top_n=2)
    top_chunks = [doc.page_content for doc, score in reranked]
    context = "\n\n".join(top_chunks)

    # Генерация ответа через LLM
    llm = request.app.state.llm
    prompt = f"""Ты — помощник по научным статьям. Твоя задача — дать короткий, точный и однозначный ответ на вопрос, используя только приведённый контекст. Нельзя продолжать диалог, нельзя задавать встречные вопросы, нельзя повторяться. Ответ должен быть строго завершён после одного абзаца.

    Вопрос:
    {req.question}
    
    Контекст:
    {context}
    
    Ответ:"""

    response = llm(prompt, max_new_tokens=256, do_sample=False)[0]['generated_text']
    raw = response[len(prompt):].strip()
    answer = trim_response(raw)

    return {
        "arxiv_id": arxiv_id,
        "question": question,
        "answer": answer,
        "chunks_used": top_chunks
    }