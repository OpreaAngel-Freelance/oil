FROM python:alpine AS base

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.1.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM base AS builder

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev

# Install Poetry with cache mount
RUN --mount=type=cache,target=/root/.cache \
    pip install "poetry==$POETRY_VERSION"

WORKDIR $PYSETUP_PATH

# Copy only dependencies definition files
COPY ./poetry.lock ./pyproject.toml ./

# Install dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --only main

FROM base AS production

# Create non-root user
RUN addgroup -S appgroup && \
    adduser -S appuser -G appgroup -h /home/appuser -s /bin/sh

# Copy only virtual environment from builder
COPY --from=builder $VENV_PATH $VENV_PATH
COPY --chown=appuser:appgroup ./app /app

# Set proper ownership and switch to non-root user
WORKDIR /app
USER appuser

# Health check using the dedicated health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/api/v1/health/ || exit 1

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8085"]