FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
    pip install python-decouple pytz telethon cryptg pyrogram

CMD ["python3", "main.py"]
