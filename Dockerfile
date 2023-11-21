FROM python:3.11@sha256:65cda34e3d3e98d0ab902c5604b76f0f1615572841827b64034490bdbac50370

ENV PYTHONIOENCODING="UTF-8"

# renovate: datasource=github-releases depName=python-poetry/poetry
ENV POETRY_VERSION=1.3.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root

COPY . /app
RUN poetry install

VOLUME /app/data
ENTRYPOINT [ "poetry", "run", "python", "-m", "discord_bot"]
