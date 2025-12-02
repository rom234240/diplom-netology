FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

WORKDIR /app/orders

EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000