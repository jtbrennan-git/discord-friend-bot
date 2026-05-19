FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git ripgrep xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh \
    | bash -s -- --skip-setup --skip-browser --hermes-home /opt/hermes-build-home

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cache buster: force rebuild
ARG CACHEBUST=1
RUN echo "Cache bust: $CACHEBUST"

COPY . .
RUN chmod +x scripts/start.sh

CMD ["./scripts/start.sh"]
