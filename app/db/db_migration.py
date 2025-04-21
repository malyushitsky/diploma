import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, ArticleMetadata, UserSession

# Пути к JSON
METADATA_PATH = "data/metadata.json"
USER_SESSIONS_PATH = "data/user_sessions.json"

# Подключение к SQLite
DB_PATH = "sqlite:///data/database.db"
engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)

# Создание таблиц
Base.metadata.create_all(engine)
session = Session()

# Загрузка metadata.json
if os.path.exists(METADATA_PATH):
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata_json = json.load(f)

    for arxiv_id, data in metadata_json.items():
        # Проверяем, существует ли уже статья
        if not session.query(ArticleMetadata).filter_by(arxiv_id=arxiv_id).first():
            session.add(ArticleMetadata(
                arxiv_id=arxiv_id,
                title=data.get("title"),
                abstract=data.get("abstract"),
                conclusion=data.get("conclusion")
            ))

# Загрузка user_sessions.json
if os.path.exists(USER_SESSIONS_PATH):
    with open(USER_SESSIONS_PATH, "r", encoding="utf-8") as f:
        user_sessions_json = json.load(f)

    for user_id, arxiv_data in user_sessions_json.items():
        arxiv_id = arxiv_data.get("arxiv_id") if isinstance(arxiv_data, dict) else arxiv_data
        if arxiv_id and not session.query(UserSession).filter_by(user_id=user_id).first():
            session.add(UserSession(user_id=user_id, arxiv_id=arxiv_id))

session.commit()
session.close()
print("✅ Миграция завершена успешно.")