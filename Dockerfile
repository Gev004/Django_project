FROM python:3.11

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY mysite/pyproject.toml mysite/poetry.lock* ./
RUN poetry install --no-root

COPY mysite/ ./
