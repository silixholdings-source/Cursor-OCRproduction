FROM grafana/k6:latest

# Install additional tools
USER root
RUN apk add --no-cache curl jq

# Set working directory
WORKDIR /load-testing

# Copy test scripts and configuration
COPY k6-*.js ./
COPY k6-config.json ./
COPY run-load-tests.sh ./

# Make script executable
RUN chmod +x run-load-tests.sh

# Set default command
CMD ["k6", "run", "k6-ocr-load-test.js"]
