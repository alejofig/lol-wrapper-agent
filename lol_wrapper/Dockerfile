FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

ENV PORT 8080

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
COPY requirements.txt ./


RUN uv pip install -r requirements.txt --system


COPY . .


EXPOSE 8080

CMD ["python",  "server_http.py"] 