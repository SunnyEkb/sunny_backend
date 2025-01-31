FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app
RUN pip3 install -U pip && \
    pip3 install -r /app/requirements.txt --no-cache-dir

COPY ./src /app
