FROM python:3-buster
ENV PYTHONIOENCODING="UTF-8"

COPY / /app/
WORKDIR /app

RUN \
 pip install --no-cache-dir -U -r /app/requirements.txt && \
 rm -rf \
   /root/.cache \
   /tmp/*

RUN \
 pip install --no-cache-dir -U -r /app/extensions/requirements.txt && \
 rm -rf \
   /root/.cache \
   /tmp/*

VOLUME /app/data
ENTRYPOINT ["python3", "/app/bot.py"]
CMD ["--data", "/app/data", "--config", "/app/data/config.yml"]
