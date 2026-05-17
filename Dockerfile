# Upgrade to Python 3.10 to satisfy package requirements
FROM python:3.10-slim

# Set working directory
WORKDIR /app/AttendX

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Prevent memory crash
ENV CMAKE_BUILD_PARALLEL_LEVEL=1

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# FIX: Give read/write permissions for Database and Images
RUN chmod -R 777 /app/AttendX

EXPOSE 7860

# Command to run attendance system (Gunicorn hata diya gaya hai)
CMD ["python", "app.py"]
