FROM python:3.12-slim

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements
COPY projects/user_service/app/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt


# Copy shared utilities
COPY shared /shared
COPY projects/user_service/app /app
COPY projects/user_service/alembic.ini /app/alembic.ini
COPY projects/user_service/alembic /app/alembic

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
