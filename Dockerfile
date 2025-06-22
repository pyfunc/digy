FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install DIGY
COPY . /app
WORKDIR /app

RUN pip install poetry && \
    poetry install

# Create a RAM disk mount point
VOLUME /tmp/digy_ram

# Set environment variables
ENV DIGY_RAM=/tmp/digy_ram
ENV PYTHONPATH=/app

# Default command
CMD ["poetry", "run", "digy"]
