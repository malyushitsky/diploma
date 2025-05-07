# 🧠 ArxivRAG: Интеллектуальная QA-система по научным статьям

---

## 📖 Описание

ArxivRAG — это современная система на базе **FastAPI** и **Telegram-бота**, которая позволяет:

- 📥 **Загружать** научные статьи с arXiv.org или PDF файлом
- 📊 **Генерировать резюме** статьи на русском языке
- ❓ **Отвечать на вопросы** по содержанию статьи на основе Retrieval-Augmented Generation (**RAG**)

---

## ✨ Особенности

- 🌍 **Поддержка русскоязычных запросов** к **англоязычным статьям**
- 🧠 **Автоматическая суммаризация** на основе разделов `Abstract` и `Conclusion` из PDF-файла
- 🤖 **Интуитивный чат-интерфейс**: навигация через кнопки в Telegram
- ⚡ **Асинхронная обработка задач** через **Celery** и **Redis** — всё работает быстро и масштабируемо
- 🏗️ **Retrieval + Rerank + Generation**:
  - Поиск релевантных фрагментов с помощью эмбеддингов **BGE-M3**
  - Повторная ранжировка через **BGE-Reranker v2**
  - Ответы генерируются через **LLM** [`Qwen 3 8B`]
- 🧩 **Кэширование и привязка** статей к `Telegram user_id` для удобного продолжения работы
- 🐳 **Готова к запуску через Docker Compose**

---

## 🚀 Инструкция по локальному запуску

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/malyushitsky/diploma.git
   ```

2. Перейдите в директорию проекта:
   ```bash
   cd diploma
   ```

3. Соберите и запустите контейнеры с помощью Docker:
   ```bash
   docker compose up --build
   ```

---

## 📚 Как пользоваться внутри ТГ бота

[👉 Запустить Telegram-бота](https://t.me/ArxivRagBot)

1. Нажмите **"⬇️ Загрузить статью"** и отправьте ссылку на arXiv (например, `https://arxiv.org/abs/2501.08248`)
2. Нажмите **"📊 Суммаризация"** — бот сгенерирует краткое резюме на русском
3. Выберите **"❓ Задать вопрос"** — и получите точный, аккуратный ответ на любой вопрос по статье

---

## 📁 Структура проекта

```text
project-root/
├── app/                     # 🧩 FastAPI-приложение
│   ├── Dockerfile           # Dockerfile для FastAPI
│   ├── main.py              # Точка входа FastAPI
│   ├── api/                 # Роуты API
│   │   ├── ingest.py        # /ingest — загрузка статьи
│   │   ├── ask.py           # /question_answer — ответ на вопрос
│   │   ├── summarize.py     # /summarize — суммаризация статьи
│   │   ├── ingest_async.py  # /ingest_async — асинхронная загрузка статьи через Celery
│   │   ├── summarize_async.py # /summarize_async — асинхронная суммаризация через Celery
│   │   ├── ask_async.py     # /ask_async — асинхронный ответ через Celery
│   ├── services/            # Логика обработки
│   │   ├── article_parser.py     # Скачивание, парсинг и очистка PDF
│   │   └── vectorstore.py        # Работа с ChromaDB + reranker
│   ├── models/
│   │   └── schemas.py       # Pydantic-схемы для запросов
│   ├── db/
│   │   ├── crud.py          # Операции с БД
│   │   ├── database.py      # Подключение к SQLite
│   │   ├── db_migration.py  # Скрипт переноса данных из старых JSON в БД
│   │   └── models.py        # SQLAlchemy модели
│	│
│	├── tasks/				 # Celery задачи
│	│	├── ask_task.py 		     
│	│	├── ingest_task.py 		 
│	│	└── summarize_task.py 	
│	│
│	└── celery_globals.py 	 # Глобальные модели (LLM, Embedder, Reranker) для Celery
│	
├── celery_app.py  		     # Настройка Celery и Redis
│
├── articles/                # 📰 Сохранённые PDF-файлы статей
│   └── <arxiv_id>.pdf
│
├── chroma_storage/          # 💾 Локальная векторная база ChromaDB
│
├── data/                    # Вспомогательные JSON-файлы
│   └── database.db          # база данных со всеми метаданными
│
├── tg_bot/                  # Telegram-бот на aiogram
│   ├── Dockerfile           # Dockerfile для Telegram-бота
│   ├── main.py              # Запуск бота
│   ├── handlers.py          # FSM-хендлеры: /start, /ingest, /summarize, /ask
│   ├── keyboards.py         # Клавиатура с командами
│   ├── states.py            # Состояния FSM
│
├── .env                     # 🔐 Токен Telegram-бота
│
├── docker-compose.yml       # 🐳 Docker Compose
├── Dockerfile               # Dockerfile для Celery worker (с GPU)
│
├── requirements/            # 📦 Зависимости по сервисам
│   ├── requirements-fastapi.txt
│   ├── requirements-celery.txt
│   └── requirements-bot.txt
│
└── README.md                # 📘 Описание проекта
```

---

## ⚙️ Технологический стек

| Компонент          | Используемые технологии            |
|--------------------|-------------------------------------|
| Web API            | **FastAPI**                         |
| Бот                | **aiogram 3** (Telegram Bot API)    |
| Фоновая обработка  | **Celery** + **Redis**              |
| Векторная БД       | **ChromaDB**                        |
| База данных        | **SQLite**     					   |
| Эмбеддер           | **BAAI/bge-m3**                     |
| Реранкер           | **BAAI/bge-reranker-v2**            |
| Генерация ответов  | **T-Bank Lite 8B (LLM)**            |

---