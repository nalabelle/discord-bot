FROM python:3.13@sha256:0a301600e451618e1c0a94c28b5d83f875f6f3c07820a71d6dd2565a000f7408

ENV PYTHONIOENCODING="UTF-8"

# renovate: datasource=github-releases depName=python-poetry/poetry
ENV POETRY_VERSION=1.8.4
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
