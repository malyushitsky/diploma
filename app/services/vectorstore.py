from langchain.vectorstores import Chroma
from langchain.text_splitter import MarkdownTextSplitter
from langchain.schema import Document
from FlagEmbedding import FlagReranker


def store_chunks(md_cleaned: str, arxiv_id: str, title: str, embedding_model, persist_directory="chroma_storage"):
    """
    Разбивает markdown на чанки и сохраняет их в ChromaDB.

    args:
        md_cleaned (str): Markdown-документ
        arxiv_id (str): ID статьи
        title (str): Заголовок статьи
        embedding_model: Инициализированная модель эмбеддингов
        persist_directory (str): Каталог для хранения Chroma

    returns:
        list[Document]: Список добавленных чанков
    """
    splitter = MarkdownTextSplitter(chunk_size=800, chunk_overlap=100)
    docs = splitter.create_documents([md_cleaned])
    for doc in docs:
        doc.metadata = {"arxiv_id": arxiv_id, "title": title}

    vectordb = Chroma.from_documents(documents=docs, embedding=embedding_model, persist_directory=persist_directory)
    vectordb.persist()
    return docs


def retrieve_and_rerank(query: str, vectordb, reranker: FlagReranker, arxiv_id: str, top_k=5, top_n=2):
    """
    Извлекает релевантные документы по конкретной статье и переранжирует их.

    args:
        query (str): Вопрос пользователя
        vectordb (Chroma): Векторная база
        reranker (FlagReranker): Модель для переранжирования
        arxiv_id (str): ID статьи для фильтрации
        top_k (int): Кол-во кандидатов
        top_n (int): Кол-во возвращаемых финальных результатов

    returns:
        list: Отсортированный список (doc, score)
    """
    retriever = vectordb.as_retriever(
        search_kwargs={"k": top_k, "filter": {"arxiv_id": arxiv_id}}
    )
    candidates = retriever.get_relevant_documents(query)

    if not candidates:
        return []

    pairs = [[query, doc.page_content] for doc in candidates]
    scores = reranker.compute_score(pairs, normalize=True)
    reranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
    return reranked[:top_n]
