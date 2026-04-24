#!/bin/sh
set -e

DATABASE_HOST=${DATABASE_HOST}
DATABASE_PORT=${DATABASE_PORT}

echo "жду пока бд поднимется..."
until nc -z -v -w3 "$DATABASE_HOST" "$DATABASE_PORT"; do
  echo "бд еще не активна, жду"
  sleep 1
done

echo "запускаю сервер..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000