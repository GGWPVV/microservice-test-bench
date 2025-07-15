FROM python:3.12-slim

WORKDIR /app

# Remove old 'jwt' package if it exists and upgrade pip
RUN pip install --upgrade pip && pip uninstall -y jwt || true

# Copy requirements.txt
COPY app/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire app and alembic config to /app
COPY app /app
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
