import json
import os
from typing import Dict

SESSION_FILE = "data/user_sessions.json"

def load_sessions() -> Dict[str, Dict]:
    """
    Загружает сессии пользователей из файла JSON.

    returns:
        dict: отображение user_id → информация о статье (например, arxiv_id)
    """
    if not os.path.exists(SESSION_FILE):
        return {}
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sessions(sessions: Dict[str, Dict]) -> None:
    """
    Сохраняет сессии пользователей в файл JSON.

    args:
        sessions (dict): отображение user_id → информация о статье
    """
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

def register_user_session(user_id: str, arxiv_id: str):
    """
    Регистрирует или обновляет сессию пользователя.

    args:
        user_id (str): Telegram user ID
        arxiv_id (str): ID загруженной статьи
    """
    sessions = load_sessions()
    sessions[user_id] = {"arxiv_id": arxiv_id}
    save_sessions(sessions)

def get_user_article(user_id: str) -> str:
    """
    Возвращает arxiv_id, ассоциированный с пользователем.

    args:
        user_id (str): Telegram user ID

    returns:
        str: arxiv_id или None, если не найден
    """
    sessions = load_sessions()
    user_data = sessions.get(user_id)
    return user_data["arxiv_id"] if user_data else None