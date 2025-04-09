import json
import os
from typing import Optional

METADATA_FILE = "data/metadata.json"


def load_metadata() -> dict:
    """
    Загружает метаинформацию из metadata.json

    returns:
        dict: Словарь с ID статей и их метаданными
    """
    if not os.path.exists(METADATA_FILE):
        return {}
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_metadata(data: dict):
    """
    Сохраняет словарь с метаданными в metadata.json

    args:
        data (dict): Словарь для сохранения
    """
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def update_metadata(arxiv_id: str, title: str, abstract: str, conclusion: str):
    """
    Добавляет или обновляет информацию о статье в metadata.json

    args:
        arxiv_id (str): ID статьи
        title (str): Название
        abstract (str): Текст аннотации
        conclusion (str): Текст заключения
    """
    data = load_metadata()
    data[arxiv_id] = {
        "title": title,
        "abstract": abstract,
        "conclusion": conclusion
    }
    save_metadata(data)


def get_section(arxiv_id: str, section: str) -> Optional[str]:
    """
    Получает abstract или conclusion по ID статьи

    args:
        arxiv_id (str): ID статьи
        section (str): 'abstract' или 'conclusion'

    returns:
        Optional[str]: Текст секции, если есть
    """
    data = load_metadata()
    return data.get(arxiv_id, {}).get(section)