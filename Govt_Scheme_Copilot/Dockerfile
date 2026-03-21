FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Download Endee binary
RUN curl -L https://github.com/endee-ai/endee/releases/latest/download/endee-linux-amd64 -o endee

# Make executable
RUN chmod +x endee

# Expose port
EXPOSE 8080

# Run Endee
CMD ["./endee"]