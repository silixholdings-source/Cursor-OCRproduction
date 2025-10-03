#!/usr/bin/env python3
import sys
import time
import urllib.request
import urllib.error

# Wait for the API to be ready
time.sleep(5)

try:
    # Make a request to the health endpoint
    response = urllib.request.urlopen("http://localhost:8000/health")
    
    # Check if the response is 200 OK
    if response.getcode() == 200:
        sys.exit(0)
    else:
        print(f"Health check failed with status code: {response.getcode()}")
        sys.exit(1)
except urllib.error.URLError as e:
    print(f"Health check failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error during health check: {e}")
    sys.exit(1)






























