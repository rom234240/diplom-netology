#!/bin/bash
# entrypoint.sh

echo "Ожидание доступности базы данных..."
while ! nc -z db 5432; do
  sleep 1
done
echo "База данных доступна!"

echo "Выполнение миграций..."
python manage.py migrate --noinput

echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

echo "Запуск сервера..."
exec "$@"