FROM python:3.10-slim

WORKDIR /code

COPY ../requirements/requirements-fastapi.txt .
RUN pip install --no-cache-dir -r requirements-fastapi.txt

COPY ../app ./app
COPY ../celery_app.py ./celery_app.py
ENV PYTHONPATH=/code

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

