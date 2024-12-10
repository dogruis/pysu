#!/bin/bash
set -e

# Ensure the working directory is the same as the script location
cd "$(dirname "$(readlink -f "$BASH_SOURCE")")"

# Enable debugging for the following commands
set -x

# Build the Docker image for the pysu project
docker build --pull -t pysu -f tests/Dockerfile.test-alpine .

# Remove any previously generated files to start fresh
rm -f pysu* SHA256SUMS*

# Run the Docker container and extract the binary (in case it’s inside the container at /app/bin or similar)
docker run --rm pysu sh -c 'cd /app/bin && tar -c pysu*' | tar -xv

# Generate SHA256 checksums for the binaries
sha256sum pysu* | tee SHA256SUMS

# Display information about the binary (similar to the `file` command in the original)
file pysu*

# List the generated files in a human-readable format
ls -lFh pysu* SHA256SUMS*

# Run the pysu binary with the appropriate architecture flag (similar to `dpkg --print-architecture` in the original script)
"./pysu-$(dpkg --print-architecture)" --help
