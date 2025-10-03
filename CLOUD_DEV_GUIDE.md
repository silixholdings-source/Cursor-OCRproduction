# Cloud Development Environment Guide

This guide provides three options for running your OCR automation project in the cloud without consuming local resources.

## Option A: GitHub Codespaces (Recommended)

GitHub Codespaces provides a full development environment in the cloud with VS Code interface.

### Setup Steps:

1. **Enable Codespaces on your repository:**
   - Go to your GitHub repository
   - Click on the "Code" button
   - Select "Codespaces" tab
   - Click "Create codespace on main"

2. **Configure the development environment:**
   Create `.devcontainer/devcontainer.json`:
   ```json
   {
     "name": "OCR Automation Service",
     "image": "mcr.microsoft.com/vscode/devcontainers/python:3.11",
     "features": {
       "ghcr.io/devcontainers/features/docker-in-docker:2": {}
     },
     "customizations": {
       "vscode": {
         "extensions": [
           "ms-python.python",
           "ms-python.flake8",
           "ms-python.black-formatter",
           "ms-toolsai.jupyter"
         ]
       }
     },
     "postCreateCommand": "sudo apt-get update && sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils",
     "forwardPorts": [8000],
     "portsAttributes": {
       "8000": {
         "label": "OCR Service",
         "onAutoForward": "notify"
       }
     }
   }
   ```

3. **Start developing:**
   - Codespace will automatically install dependencies
   - Run `python main.py` to start the service
   - Access at `https://your-codespace-url-8000.preview.app.github.dev`

### Pros:
- Full VS Code experience
- Pre-configured environment
- Easy sharing and collaboration
- Free tier available (120 hours/month)

### Cons:
- Requires GitHub account
- Limited free hours
- Internet dependency

## Option B: Render Background Worker for Development

Use Render's background worker service for development builds.

### Setup Steps:

1. **Create a development service in Render:**
   - Go to Render Dashboard
   - Create new "Background Worker"
   - Connect your GitHub repository
   - Use branch `develop` or `dev`

2. **Configure render-dev.yaml:**
   ```yaml
   services:
     - type: worker
       name: ocr-dev-worker
       env: docker
       dockerfilePath: ./Dockerfile
       plan: starter
       branch: develop
       envVars:
         - key: ENVIRONMENT
           value: development
         - key: DEBUG
           value: true
   ```

3. **Access via Render's built-in terminal:**
   - Use Render's web-based terminal
   - Run development commands
   - Monitor logs in real-time

### Pros:
- Persistent environment
- Built-in monitoring
- Easy scaling
- Professional infrastructure

### Cons:
- Costs money (even on starter plan)
- Less interactive than full IDE
- Limited customization

## Option C: Docker with Remote Containers

Use Docker with VS Code Remote Containers for local-like development in the cloud.

### Setup Steps:

1. **Create docker-compose.dev.yml:**
   ```yaml
   version: '3.8'
   services:
     ocr-dev:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - .:/app
         - /app/__pycache__
       environment:
         - ENVIRONMENT=development
         - DEBUG=true
       command: python main.py
       stdin_open: true
       tty: true
   ```

2. **Deploy to cloud provider with Docker support:**
   - **Railway**: Connect GitHub, auto-deploy
   - **Fly.io**: `fly launch` with Dockerfile
   - **DigitalOcean App Platform**: Docker container option

3. **Connect VS Code Remote Containers:**
   - Install "Remote - Containers" extension
   - Connect to remote container
   - Full VS Code experience

### Pros:
- Full IDE experience
- Local development workflow
- Multiple cloud provider options
- Cost-effective

### Cons:
- Requires Docker knowledge
- Setup complexity
- Provider-specific configurations

## Quick Start Commands

### GitHub Codespaces:
```bash
# In Codespace terminal
pip install -r requirements.txt
sudo apt-get install -y tesseract-ocr poppler-utils
python main.py
```

### Render Development:
```bash
# Via Render terminal
python main.py
# Service will be available at Render-provided URL
```

### Docker Remote:
```bash
# On cloud provider
docker-compose -f docker-compose.dev.yml up
# Connect VS Code Remote Containers
```

## Environment Variables for Development

Create `.env.dev`:
```env
ENVIRONMENT=development
DEBUG=true
OCR_PROVIDER=tesseract
CONFIDENCE_THRESHOLD=0.8
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png,tiff
```

## Testing in Cloud Environment

### Run Tests:
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
python -m pytest test_ocr.py -v

# Run with coverage
python -m pytest test_ocr.py --cov=main --cov-report=html
```

### Test OCR Endpoint:
```bash
# Health check
curl https://your-service-url/health

# Test OCR with sample image
curl -X POST "https://your-service-url/ocr" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.png" \
  -F "language=eng"
```

## Switching Between Environments

### Local Development:
```bash
# Activate virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

### Cloud Development:
```bash
# Use any of the three options above
# Environment is already configured
# Just run: python main.py
```

## Cost Comparison

| Option | Free Tier | Paid Plans | Best For |
|--------|-----------|------------|----------|
| GitHub Codespaces | 120 hours/month | $0.18/hour | Individual developers |
| Render | $7/month | $7-25/month | Teams, production-like |
| Docker Remote | Varies by provider | $5-20/month | Custom setups |

## Recommendations

1. **For beginners**: GitHub Codespaces
2. **For teams**: Render with background workers
3. **For advanced users**: Docker with cloud providers
4. **For production**: Use the main Render service with `render.yaml`

Choose the option that best fits your workflow, budget, and technical requirements!
