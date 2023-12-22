FROM python:3.10-slim

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
