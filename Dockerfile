# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies for DeepFace/OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Copy UI files
COPY index.html ./
COPY upload.html ./
COPY match.html ./
COPY list.html ./
COPY delete.html ./
COPY stats.html ./

# Expose the port for the lightning fast API (default: 8001)
EXPOSE 8001

# Start the API (change to api_arcface_standalone.py and port 8002 if needed)
CMD ["python", "api/main_arface2.py"]
