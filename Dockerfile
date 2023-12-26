FROM python:3.11@sha256:4e5e9b05dda9cf699084f20bb1d3463234446387fa0f7a45d90689c48e204c83

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
