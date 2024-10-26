FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/bd_backup

ENV PYTHONIOENCODING=utf-8

EXPOSE 8000

CMD ["python", "bot.py"]
