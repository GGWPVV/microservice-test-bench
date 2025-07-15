FROM python:3.12

# Рабочая директория для приложения
WORKDIR /app

# Копируем requirements.txt из app в контейнер
COPY app/requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем весь код приложения
COPY app /app

# Копируем alembic.ini и папку миграций в корень контейнера
COPY alembic.ini /alembic.ini
COPY alembic /alembic

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
