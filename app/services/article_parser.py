import re
import requests
from typing import Optional, List, Tuple
import arxiv
import pymupdf4llm

def extract_arxiv_id(url: str) -> str:
    """
    Извлекает arXiv ID из URL.

    Args:
        url (str): Ссылка на статью arXiv.

    Returns:
        str: Извлечённый ID или None, если не удалось.
    """
    match = re.search(r'arxiv\.org/(abs|pdf)/([0-9]+\.[0-9]+)(v\d+)?', url)
    return match.group(2) if match else None


def download_pdf(arxiv_id: str, save_path: str = "article.pdf") -> str:
    """
    Скачивает PDF-файл по arXiv ID и сохраняет на диск.

    Args:
        arxiv_id (str): Идентификатор статьи на arXiv.
        save_path (str): Путь, по которому сохранить файл.

    Returns:
        Tuple[str, str]: Путь до сохранённого файла и название статьи.
    """
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    result = next(client.results(search))
    pdf_url = result.pdf_url

    response = requests.get(pdf_url)
    with open(save_path, "wb") as f:
        f.write(response.content)
    return save_path, result.title
    

def trim_markdown_after_section(md_text: str, section="references", aliases: Optional[List[str]] = None) -> str:
    """
    Удаляет всё из markdown-текста начиная с указанной секции (по умолчанию — References).

    Args:
        md_text (str): Исходный Markdown.
        section (str): Основной заголовок для поиска.
        aliases (List[str]): Альтернативные варианты заголовка.

    Returns:
        str: Markdown до найденного заголовка.
    """
    all_keys = [section.lower()] + [a.lower() for a in aliases or []]

    pattern = re.compile(
        rf'^#+\s*\**({"|".join(map(re.escape, all_keys))})\**.*$',
        re.IGNORECASE | re.MULTILINE
    )
    match = pattern.search(md_text)
    return md_text[:match.start()] if match else md_text


def clean_markdown_for_rag(md_raw: str) -> str:
    """
    Очищает markdown от визуального мусора, лишних символов и пустых строк.

    Args:
        md_text (str): Исходный Markdown текст.

    Returns:
        str: Очищенный и нормализованный Markdown.
    """
    lines = md_raw.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped == "-----":
            continue

        if re.fullmatch(r'[\d\s\.,%]+', stripped):
            continue

        line = re.sub(r'\*\[(,|\*|\d+)\]\*', '', line)
        line = re.sub(r'\*(,+|\s*[,\.])\*', '', line)
        line = re.sub(r'^(#{1,6})\s*\*\*(.*?)\*\*\s*$', r'\1 \2', line)
        line = re.sub(r'\*{3,}', '**', line)
        line = re.sub(r'\s{2,}', ' ', line)

        cleaned_lines.append(line)

    # Склеиваем обратно и нормализуем множественные пустые строки
    cleaned_text = "\n".join(cleaned_lines)

    # Заменяем 3+ пустых строк подряд на 2
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

    return cleaned_text

def extract_section(md_text: str, section: str, aliases: Optional[List[str]] = None) -> str:
    """
    Извлекает текст секции по заголовку, учитывая альтернативные варианты.

    Args:
        md_text (str): Markdown-документ.
        section (str): Название секции.
        aliases (List[str]): Возможные альтернативы (например, 'summary' для 'abstract').

    Returns:
        str: Извлечённый текст секции.
    """
    lines = md_text.splitlines()
    start_idx, end_idx = None, None

    all_keys = [section.lower()] + [a.lower() for a in aliases or []]

    # 1. Найдём заголовок секции
    for i, line in enumerate(lines):
        line_clean = re.sub(r'[\*\#]', '', line).strip().lower()
        for key in all_keys:
            if re.match(rf'^(\d+[\.\d+]*)?\s*{re.escape(key)}$', line_clean):
                start_idx = i + 1
                break
        if start_idx:
            break

    if start_idx is None:
        return ""

    # 2. Поиск конца секции — следующего заголовка
    for j in range(start_idx, len(lines)):
        next_line_clean = re.sub(r'[\*\#]', '', lines[j]).strip().lower()
        if re.match(r'^(\d+[\.\d+]*)?\s+\w+', next_line_clean):
            end_idx = j
            break

    section_lines = lines[start_idx:end_idx] if end_idx else lines[start_idx:]
    return "\n".join(section_lines).strip()

def parse_and_split_article(arxiv_url: str) -> Tuple[str, str, str, List]:
    """
    Загружает статью по ссылке arXiv, парсит её, очищает и разбивает на чанки.

    Returns:
        arxiv_id (str): ID статьи с arxiv.org
        title (str): Название статьи
        abstract (str): Извлечённый текст из раздела Abstract
        conclusion (str): Извлечённый текст из раздела Conclusion
    """
    arxiv_id = extract_arxiv_id(arxiv_url)
    pdf_path, title = download_pdf(arxiv_id, save_path=f"articles/{arxiv_id}.pdf")
    md_raw = pymupdf4llm.to_markdown(pdf_path)
    md_trimmed = trim_markdown_after_section(md_raw)
    md_cleaned = clean_markdown_for_rag(md_trimmed)
    abstract = extract_section(md_cleaned, "abstract", ["absctract", "summary"])
    conclusion = extract_section(md_cleaned, "conclusion", ["conclusions", "closing remarks"])

    return arxiv_id, title, md_cleaned, abstract, conclusion