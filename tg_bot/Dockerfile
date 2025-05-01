FROM python:3.10-slim

WORKDIR /code

COPY ../requirements/requirements-bot.txt .
RUN pip install --no-cache-dir -r requirements-bot.txt

COPY . /code/tg_bot

ENV PYTHONPATH=/code

CMD ["python", "tg_bot/main.py"]