# Build stage
FROM gcc:latest AS builder
WORKDIR /app
COPY src/ ./src
COPY Makefile .
# Compile the server
RUN make

# Runtime stage
FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/redis_server .
EXPOSE 1234
CMD ["./redis_server"]
