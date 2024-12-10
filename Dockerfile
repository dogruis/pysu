# Use Python 3.12 Alpine image as the base
FROM python:3.12-alpine

# Install necessary dependencies
RUN apk update && apk add --no-cache \
    bash \
    shadow \
    file \
    libc6-compat \
    && rm -rf /var/cache/apk/*

# Set unbuffered mode to ensure immediate output in logs
ENV PYTHONUNBUFFERED=1
ENV BUILD_FLAGS="-v -trimpath"

# Copy the pysu script into the container
WORKDIR /app
COPY pysu.py .

# Make the pysu script executable
RUN chmod +x /app/pysu.py

# Add a non-root user for testing (we will use the 'dogruis' user in this example)
RUN addgroup -g 1000 testgroup && \
    adduser -u 1000 -G testgroup -D dogruis
# Build and test the Python script
RUN set -eux; \
    echo '#!/usr/bin/env bash'; \
    echo 'set -Eeuo pipefail -x'; \
    echo 'python3 /app/pysu.py dogruis id'; \
    echo 'file /app/pysu.py'; \
    echo 'try() { for (( i = 0; i < 30; i++ )); do if timeout 1s "$@"; then return 0; fi; done; return 1; }'; \
    echo 'try python3 /app/pysu.py dogruis ls -l /proc/self/fd'; \
    echo 'fi' > /usr/local/bin/pysu-build-and-test.sh; \
    chmod +x /usr/local/bin/pysu-build-and-test.sh

# Disable CGO for Python binary compatibility
ENV CGO_ENABLED 0

# Testing for different architectures (similar to Go's test process)
RUN ARCH=amd64 pysu-build-and-test.sh
RUN ARCH=arm64 pysu-build-and-test.sh

# Ensure testing has completed correctly
RUN set -eux; ls -lAFh /app/pysu.py
