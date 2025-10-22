# Use an official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Set working directory
WORKDIR /app

# Copy Python package files
COPY setup.py pyproject.toml /app/
COPY cli.py utils.py /app/
# COPY .env.example /app/.env   # optional

# Install build tools
RUN pip install --upgrade pip setuptools wheel

# Install dependencies
RUN pip install .

# Make CLI executable
ENTRYPOINT ["blnd"]
CMD ["--help"]
