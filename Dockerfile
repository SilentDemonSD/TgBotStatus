FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
    pip install python-decouple pytz telethon cryptg

COPY run.sh /app/run.sh

RUN chmod +x /app/run.sh

COPY cron.txt /etc/cron.d/cron.txt

RUN chmod 0644 /etc/cron.d/cron.txt

RUN crontab /etc/cron.d/cron.txt

RUN touch /var/log/cron.log

CMD cron && tail -f /var/log/cron.log
