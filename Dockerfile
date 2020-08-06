FROM python:3-slim-buster
ENV PYTHONIOENCODING="UTF-8"

COPY / /app/
WORKDIR /app

# install app
RUN \
 pip install --no-cache-dir -U -r /app/requirements.txt && \
 rm -rf \
   /root/.cache \
   /tmp/*

VOLUME /app/data
CMD ["python3", "/app/bot.py", "--data", "/app/data", "--config", "/app/data/config.yml"]
