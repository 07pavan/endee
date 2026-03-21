FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Download correct binary (FIXED VERSION)
RUN curl -L https://github.com/endee-ai/endee/releases/download/v0.1.0/endee-linux-amd64 -o endee

RUN chmod +x endee

EXPOSE 8080

CMD ["./endee"]