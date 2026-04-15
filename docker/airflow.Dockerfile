FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ENV AIRFLOW_HOME=/app/airflow

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir apache-airflow[postgres]
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "airflow", "standalone" ]