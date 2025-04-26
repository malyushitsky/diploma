from celery_app import celery
from app.db.database import SessionLocal
from app.db.crud import get_user_arxiv_id
from app.services.vectorstore import retrieve_and_rerank
from app.celery_globals import llm, vectorstore, reranker  

def trim_response(raw: str) -> str:
    """
    Обрезает вывод модели
    
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

@celery.task
def ask_article_task(user_id: str, question: str) -> dict:
    """
    Фоновая задача: отвечает на вопрос пользователя по статье.

    args:
        user_id (str): id пользователя
        question (str
    """
    db = SessionLocal()
    try:
        arxiv_id = get_user_arxiv_id(db, user_id)
        if not arxiv_id:
            return {"error": "Вы ещё не загрузили статью. Сначала загрузите её, а потом задавайте вопросы!"}

        # Поиск релевантных документов
        reranked = retrieve_and_rerank(question, vectorstore, reranker, arxiv_id, top_k=10, top_n=2)
        top_chunks = [doc.page_content for doc, score in reranked]
        context = "\n\n".join(top_chunks)

        # Генерация ответа через LLM
        prompt = f"""Ты — помощник по научным статьям. Твоя задача — дать короткий, точный и однозначный ответ на вопрос, используя только приведённый контекст. Нельзя продолжать диалог, нельзя задавать встречные вопросы, нельзя повторяться. Ответ должен быть строго завершён после одного абзаца.

Вопрос:
{question}

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
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()