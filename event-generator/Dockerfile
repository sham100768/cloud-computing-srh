FROM python:3.12-slim

WORKDIR /app
COPY requirements-sinks.txt .
RUN pip install --no-cache-dir -r requirements-sinks.txt
COPY generator ./generator

# Run as a non-root user
RUN useradd --create-home app
USER app

# Configure with environment variables: SINK, RATE, MODE, KAFKA_BOOTSTRAP, ...
ENTRYPOINT ["python", "-m", "generator"]
CMD ["stream"]
