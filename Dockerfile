FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /vol/web/media /vol/web/static && \
    adduser \
        --disabled-password \
        --no-create-home \
        --gecos "" \
        django-user && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol/web

USER django-user