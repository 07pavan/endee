FROM golang:1.22

WORKDIR /app

# Clone Endee repo
RUN git clone https://github.com/endee-ai/endee.git .

# Build Endee
RUN go build -o endee

# Expose port
EXPOSE 8080

# Run
CMD ["./endee"]