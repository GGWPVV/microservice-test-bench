FROM python:3.12-slim

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements
COPY projects/discount_service/app/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY shared /shared
COPY projects/discount_service/app /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
