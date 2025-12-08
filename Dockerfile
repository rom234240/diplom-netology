FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    bash

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/orders

# Создаем директорию для статики
RUN mkdir -p staticfiles media static

EXPOSE 8000

# Команда по умолчанию (для web сервиса)
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]