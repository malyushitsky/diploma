from sqlalchemy.orm import Session
from app.db.models import ArticleMetadata, UserSession
from typing import Optional


def get_user_arxiv_id(db: Session, user_id: str) -> Optional[str]:
    """
    Получает arxiv_id, связанный с user_id.

    args:
        db (Session): Сессия SQLAlchemy
        user_id (str): Telegram user ID

    returns:
        Optional[str]: arxiv_id статьи, если найден
    """
    session = db.query(UserSession).filter_by(user_id=user_id).first()
    return session.arxiv_id if session else None


def get_article_by_id(db: Session, arxiv_id: str) -> Optional[ArticleMetadata]:
    """
    Получает объект статьи по arxiv_id.

    args:
        db (Session): Сессия SQLAlchemy
        arxiv_id (str): ID статьи

    returns:
        Optional[ArticleMetadata]: Объект статьи или None
    """
    return db.query(ArticleMetadata).filter_by(arxiv_id=arxiv_id).first()


def save_article_metadata(db: Session, arxiv_id: str, title: str, abstract: str, conclusion: str):
    """
    Сохраняет или обновляет метаданные статьи.

    args:
        db (Session): Сессия SQLAlchemy
        arxiv_id (str): ID статьи
        title (str): Заголовок
        abstract (str): Аннотация
        conclusion (str): Заключение
    """
    article = get_article_by_id(db, arxiv_id)
    if article:
        article.title = title
        article.abstract = abstract
        article.conclusion = conclusion
    else:
        article = ArticleMetadata(
            arxiv_id=arxiv_id,
            title=title,
            abstract=abstract,
            conclusion=conclusion
        )
        db.add(article)
    db.commit()


def register_user_session(db: Session, user_id: str, arxiv_id: str):
    """
    Регистрирует или обновляет сессию пользователя.

    args:
        db (Session): Сессия SQLAlchemy
        user_id (str): Telegram user ID
        arxiv_id (str): ID статьи
    """
    session = db.query(UserSession).filter_by(user_id=user_id).first()
    if session:
        session.arxiv_id = arxiv_id
    else:
        session = UserSession(user_id=user_id, arxiv_id=arxiv_id)
        db.add(session)
    db.commit()
