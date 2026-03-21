FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Detect architecture and download correct binary
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        curl -L https://github.com/endee-ai/endee/releases/latest/download/endee-linux-amd64 -o endee; \
    elif [ "$ARCH" = "aarch64" ]; then \
        curl -L https://github.com/endee-ai/endee/releases/latest/download/endee-linux-arm64 -o endee; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi

RUN chmod +x endee

EXPOSE 8080

CMD ["./endee"]