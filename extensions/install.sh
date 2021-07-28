#!/bin/bash
CONTAINER=$(docker ps -q -f name=discord-bot)
if [ -n "$CONTAINER" ]; then
  echo "running in $CONTAINER"
  docker exec -it $(docker ps -q -f name=discord-bot) pip install -U -t /app/data/extensions/site-packages -r /app/data/extensions/requirements.txt
fi;
