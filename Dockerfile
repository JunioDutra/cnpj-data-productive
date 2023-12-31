FROM python:3.8-slim-buster as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.8-slim-buster

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.8/site-packages/ /usr/local/lib/python3.8/site-packages/
COPY --from=builder /app /app
COPY . .

RUN mkdir -p /opt/data/download
RUN mkdir -p /opt/data/final-files