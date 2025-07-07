# Use multi-stage build for production
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for DeepFace/OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY api/ ./api/
COPY ui_batch_upload.py ./
COPY ui_flatten_images.py ./
COPY requirements.txt ./

# Copy UI files for static serving
COPY index.html ./
COPY upload.html ./
COPY match.html ./
COPY list.html ./
COPY delete.html ./
COPY stats.html ./

# Create Testing images directory
RUN mkdir -p "Testing images"

# Set environment variable for Docker
ENV DOCKER_ENV=true

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8002/ || exit 1

# Non-root user for security
RUN adduser --disabled-password --gecos '' --uid 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Start the API
CMD ["python", "api/main_arcface2.py"]
