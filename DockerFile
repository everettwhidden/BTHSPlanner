FROM python:3.11-slim
WORKDIR /app
ARG NODE_VERSION=20.x

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION} | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --home /app reflex

RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=reflex:reflex . /app
RUN chown -R reflex:reflex /app
USER reflex

RUN pip install --no-cache-dir -r requirements.txt

RUN reflex init

EXPOSE 3000
EXPOSE 8000

CMD ["reflex", "run", "--env", "prod"]