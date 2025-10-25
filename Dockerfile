# Use an official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Set working directory
WORKDIR /app

# Set up environment
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV BLONDE_HOME=/home/blonde/.blonde

# Switch to non-root user
USER blonde

# Create workspace directory
WORKDIR /workspace
VOLUME ["/workspace", "/home/blonde/.blonde"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD blnd --help || exit 1

# Default command
ENTRYPOINT ["blnd"]
CMD ["--help"]

# Labels for metadata
LABEL maintainer="Cerekin <support@cerekin.com>"
LABEL description="BlondE-CLI - AI-powered code assistant with memory and agentic capabilities"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/cerekin/blonde-cli"
LABEL org.opencontainers.image.licenses="MIT"
