FROM python:3.10-slim

WORKDIR /code

RUN pip install --no-cache-dir fastapi uvicorn

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
