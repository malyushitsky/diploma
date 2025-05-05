from typing import List
from celery_app import celery
from app.db.database import SessionLocal
from app.db.crud import get_user_arxiv_id
from app.services.vectorstore import retrieve_and_rerank
from app.celery_globals import llm, vectorstore, reranker, tokenizer

SYSTEM_MSG = (
    "Ты — помощник по научным статьям. "
    "Твоя задача — дать короткий, точный и однозначный ответ на вопрос, "
    "используя только приведённый контекст. "
    "Отвечай строго на русском языке"
)

def build_messages(question: str, context: str) -> List[dict]:
    """Формирует сообщения в нужном для chat_template формате."""
    return [
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user", "content": f"Вопрос:\n{question}"},
        {"role": "system", "content": f"Контекст:\n{context}"},
    ]



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

        # Используем chat_template
        messages = build_messages(question, context)
        messages = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)

        # Генерация ответа через LLM
        answer = llm(messages, max_new_tokens=256, temperature=0.7, top_p=0.8, top_k=20, min_p=0)[0]['generated_text']

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