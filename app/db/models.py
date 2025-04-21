from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ArticleMetadata(Base):
    __tablename__ = "article_metadata"

    arxiv_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    abstract = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)


class UserSession(Base):
    __tablename__ = "user_sessions"

    user_id = Column(String, primary_key=True, index=True)
    arxiv_id = Column(String, nullable=False)