FROM python:3.12-slim

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements
COPY projects/analytics_service/app/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY shared /shared
COPY projects/analytics_service/app /app

EXPOSE 8000

CMD python health_server.py