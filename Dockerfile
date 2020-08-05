FROM python:3-slim-buster

# set python to use utf-8 rather than ascii.
ENV PYTHONIOENCODING="UTF-8"

ENV GOOGLE_API_KEY=""
ENV FORECAST_API_KEY=""
ENV DISCORD_TOKEN=""

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

# install app
RUN \
 echo "**** install pip packages ****" && \
 pip install --no-cache-dir -U -r /app/requirements.txt && \
 echo "**** cleanup ****" && \
 rm -rf \
   /root/.cache \
   /tmp/*

# add local files
COPY bot/ /app/
VOLUME /app/config
CMD ["python3", "/app/bot.py", "--config", "/app/config/config.yml"]
