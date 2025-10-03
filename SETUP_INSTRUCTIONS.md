# OCR Automation Project Setup Instructions

## 🚀 Quick Setup Guide

Follow these steps to get your OCR automation project running with GitHub and Render.

## 1. GitHub Integration

### Initialize Git Repository

```bash
# Initialize git in your project folder
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: OCR automation service with FastAPI"

# Connect to GitHub (replace with your repository URL)
git remote add origin https://github.com/yourusername/ocr-automation-project.git

# Push to GitHub
git push -u origin main
```

### Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and create a new repository
2. Name it `ocr-automation-project` (or your preferred name)
3. Don't initialize with README (we already have files)
4. Copy the repository URL and use it in the commands above

## 2. Render Deployment Setup

### Create Render Account

1. Go to [Render.com](https://render.com) and sign up
2. Connect your GitHub account
3. Create a new Web Service

### Configure Render Service

1. **Connect Repository**: Select your GitHub repository
2. **Configure Service**:
   - **Name**: `ocr-automation-service`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
   - **Docker Context**: `.`
   - **Plan**: Starter (Free)
   - **Region**: Oregon (or closest to you)

3. **Environment Variables** (Optional):
   ```
   ENVIRONMENT=production
   OCR_PROVIDER=tesseract
   CONFIDENCE_THRESHOLD=0.8
   MAX_FILE_SIZE=10485760
   ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png,tiff
   ```

4. **Auto-Deploy**: Enable automatic deployments from main branch

### Get Render API Credentials

1. Go to your Render Dashboard
2. Click on your service
3. Go to "Settings" → "API Keys"
4. Copy your API key
5. Note your service ID from the URL

## 3. GitHub Actions Setup

### Add Repository Secrets

1. Go to your GitHub repository
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Add these secrets:

```
RENDER_API_KEY=your-render-api-key
RENDER_SERVICE_ID=your-render-service-id
```

### Verify Workflow

The workflow will automatically run on:
- Push to `main` branch
- Pull requests to `main` branch

## 4. Local Development Setup

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized development)
- Git

### Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Install System Dependencies

#### Windows:
```bash
# Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR

# Install Poppler (for PDF processing)
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
# Add to PATH: C:\poppler-XX.XX.X\Library\bin
```

#### macOS:
```bash
brew install tesseract poppler
```

#### Linux:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng poppler-utils
```

### Run the Service

```bash
# Start the OCR service
python main.py

# Service will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

## 5. Testing Your Setup

### Test Local Service

```bash
# Health check
curl http://localhost:8000/health

# Test with a sample image (replace with actual image path)
curl -X POST "http://localhost:8000/ocr" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.png" \
  -F "language=eng"
```

### Test Render Deployment

```bash
# Replace with your Render service URL
curl https://your-service-name.onrender.com/health
```

### Run Tests

```bash
# Run the test suite
python test_ocr.py

# Or with pytest
python -m pytest test_ocr.py -v
```

## 6. Cloud Development Options

See `CLOUD_DEV_GUIDE.md` for detailed instructions on:

- **GitHub Codespaces**: Full cloud IDE
- **Render Background Workers**: Development builds
- **Docker Remote Containers**: VS Code in the cloud

## 7. Production Checklist

- [ ] Environment variables configured
- [ ] Health checks working
- [ ] OCR processing tested
- [ ] GitHub Actions pipeline running
- [ ] Render deployment successful
- [ ] SSL certificate configured (automatic on Render)
- [ ] Monitoring setup (optional)

## 8. API Usage Examples

### Upload and Process Document

```bash
curl -X POST "https://your-service.onrender.com/ocr" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@invoice.pdf" \
  -F "language=eng" \
  -F "confidence_threshold=0.8"
```

### Response Format

```json
{
  "success": true,
  "text": "Extracted text from document...",
  "confidence": 0.95,
  "processing_time": 2.3,
  "file_type": "pdf",
  "error": null
}
```

## 9. Troubleshooting

### Common Issues

1. **Tesseract not found**: Install Tesseract OCR system package
2. **PDF processing fails**: Install Poppler utilities
3. **Docker build fails**: Check Dockerfile and system dependencies
4. **Render deployment fails**: Check logs in Render dashboard
5. **GitHub Actions fails**: Verify secrets are set correctly

### Getting Help

1. Check the logs in Render dashboard
2. Review GitHub Actions workflow runs
3. Test locally first before deploying
4. Check the FastAPI docs at `/docs` endpoint

## 10. Next Steps

1. **Add Azure Form Recognizer**: For production-grade OCR
2. **Implement authentication**: Add API keys or JWT
3. **Add database**: Store processing results
4. **Add monitoring**: Implement logging and metrics
5. **Scale up**: Upgrade Render plan for higher traffic

## Support

- **Documentation**: Check `/docs` endpoint when service is running
- **Issues**: Create GitHub issues for bugs or feature requests
- **Render Support**: Use Render's support system for deployment issues

Happy coding! 🎉
