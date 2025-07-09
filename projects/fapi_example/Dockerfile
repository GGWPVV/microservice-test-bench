FROM python:3.13-slim

WORKDIR /app

ARG packages=fapi_example-0.1.0-py3-none-any.whl
COPY dist/$packages .

RUN pip install --upgrade --no-cache-dir $packages

EXPOSE 8000

CMD ["uvicorn", "backend.fapi_example.core:app", "--host", "0.0.0.0", "--port", "8000"]
