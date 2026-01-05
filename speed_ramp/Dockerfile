# Use official slim Python image
FROM python:3.13-slim

WORKDIR /app

# Install ffmpeg and basic tools
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     ffmpeg \
     curl \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user and set ownership
RUN groupadd -r app && useradd -r -g app app \
  && chown -R app:app /app
USER app

EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "speedramp:app", "--host", "0.0.0.0", "--port", "8000"]