#!/bin/bash
CONTAINER=$(docker ps -q -f name=discord-bot)
if [ -n "$CONTAINER" ]; then
  echo "running in $CONTAINER"
  docker exec -it $(docker ps -q -f name=discord-bot) /bin/bash -c 'PYTHONPATH="/app/data/extensions/site-packages:/app/shared:/app/data/extensions/" python3 -m pytest -o log_level=debug -o log_cli=True -o cache_dir=/tmp/pytest_cache --ignore=data/extensions/site-packages --pyargs -v /app/data/extensions/'
fi;
