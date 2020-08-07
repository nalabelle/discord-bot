FROM python:3-slim-buster
ENV PYTHONIOENCODING="UTF-8"

COPY / /app/
WORKDIR /app

# install app
RUN \
 pip install --no-cache-dir -U -r /app/requirements.txt && \
 pip install -e shared/*/
 rm -rf \
   /root/.cache \
   /tmp/*

VOLUME /app/data
ENTRYPOINT ["python3", "/app/bot.py"]
CMD ["--data", "/app/data", "--config", "/app/data/config.yml"]
