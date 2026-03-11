FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install uv (fast Python dependency manager).
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -s /root/.local/bin/uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 8000

# Keep the container running and execute commands manually in the course.
CMD ["sh", "-c", "tail -f /dev/null"]
