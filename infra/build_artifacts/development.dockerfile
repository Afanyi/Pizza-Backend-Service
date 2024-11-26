# Layers: Only RUN, COPY, and ADD create layers.

ARG PYTHON_IMAGE_VERSION=3.10

# Target: development
FROM python:${PYTHON_IMAGE_VERSION}-slim-buster AS development

# Environment variables
ENV USER_ID=1000
ENV GROUP_ID=1000
ENV USER=web
ENV HOME="/${USER}"

ENV \
    POETRY_VERSION=1.5.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VENV_PATH="${HOME}/.venv" \
    PATH="$HOME/.local/bin:$VENV_PATH/bin:$PATH" \
    PYTHONHASHSEED=1

# Install necessary dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gnupg build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create user and group
RUN addgroup --gid ${GROUP_ID} ${USER} \
    && adduser --disabled-password --gecos '' --home "${HOME}" --uid "${USER_ID}" --gid "${GROUP_ID}" "${USER}"

# Switch to the non-root user
USER ${USER}
WORKDIR ${HOME}

# Install Poetry
RUN pip install --user poetry==${POETRY_VERSION}

# Copy pyproject.toml and poetry.lock with proper ownership
COPY --chown=${USER_ID}:${GROUP_ID} ./pyproject.toml ./poetry.lock ${HOME}/

# Install dependencies using Poetry
RUN poetry install

# Replace psycopg2-binary with psycopg2
RUN pip uninstall psycopg2-binary -y \
    && pip install psycopg2

# Copy application code
COPY --chown=${USER_ID}:${GROUP_ID} ./app ${HOME}/app/

# Copy the entrypoint script with secure permissions
COPY --chown=${USER_ID}:${GROUP_ID} ./infra/build_artifacts/docker-entrypoint.sh ${HOME}/scripts/
RUN chmod 0555 ${HOME}/scripts/docker-entrypoint.sh

# Copy additional configuration and tests with proper ownership
COPY --chown=${USER_ID}:${GROUP_ID} ./alembic.ini ${HOME}/
COPY --chown=${USER_ID}:${GROUP_ID} ./tests ${HOME}/tests/

# Ensure scripts directory has secure permissions
RUN chmod -R 0755 ${HOME}/scripts

# Expose application port
EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["./scripts/docker-entrypoint.sh"]
