# syntax=docker/dockerfile:1.7
# API image for the drawing-review service (CPU; stub or remote backends).
# For a production build, pin the base image by digest as well as by tag.

FROM python:3.11.10-slim-bookworm AS build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /src
COPY requirements.lock ./
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --no-deps -r requirements.lock
COPY pyproject.toml README.md ./
COPY src ./src
RUN /opt/venv/bin/pip install --no-deps .

FROM python:3.11.10-slim-bookworm
ARG GIT_SHA=unknown
LABEL org.opencontainers.image.source="https://github.com/lyftium/drawing-review-service" \
      org.opencontainers.image.revision="${GIT_SHA}"
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DRW_GIT_SHA=${GIT_SHA}
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
COPY --from=build /opt/venv /opt/venv
# The golden reference set ships with the image so the eval Job can run anywhere.
# Only labels and expected outputs are in git; the drawings are generated here.
COPY golden /app/golden
RUN drawing-review golden --dir /app/golden
WORKDIR /app
USER 10001:10001
EXPOSE 8080
# No shell form: signals reach uvicorn directly for graceful shutdown.
CMD ["uvicorn", "--factory", "drawing_review.api:app_factory", "--host", "0.0.0.0", "--port", "8080", "--no-access-log"]
