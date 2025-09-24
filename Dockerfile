# Lightweight container for the mini pipeline
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (git for yfinance fallback if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install core deps; To enable NLP inside container, pass --build-arg ENABLE_NLP=1 at build time.
ARG ENABLE_NLP=0
RUN if [ "$ENABLE_NLP" = "1" ]; then \
        pip install --no-cache-dir ".[nlp]" -r requirements.txt ; \
    else \
        pip install --no-cache-dir -r requirements.txt ; \
    fi

COPY src/ ./src/

WORKDIR /app/src

# Expose Streamlit's default port
EXPOSE 8501

# Launch the UI by default
CMD ["streamlit", "run", "app_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]