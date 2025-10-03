#!/bin/sh
# Simple health check script for Docker health check

# Wait for the API to be ready
sleep 5

# Make a request to the health endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

# Check if the response is 200 OK
if [ "$response" = "200" ]; then
    exit 0
else
    exit 1
fi






























