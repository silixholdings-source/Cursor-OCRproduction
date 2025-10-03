# Windows Setup Instructions for OCR Automation Project

## Prerequisites Installation

### 1. Install Git for Windows

1. Download Git from: https://git-scm.com/download/win
2. Run the installer with default settings
3. Restart your terminal/PowerShell after installation

### 2. Install Python 3.11+

1. Download Python from: https://www.python.org/downloads/
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```powershell
   python --version
   pip --version
   ```

### 3. Install Tesseract OCR

1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install with default settings
3. Add to PATH: `C:\Program Files\Tesseract-OCR`
4. Verify installation:
   ```powershell
   tesseract --version
   ```

### 4. Install Poppler (for PDF processing)

1. Download from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to `C:\poppler-XX.XX.X`
3. Add to PATH: `C:\poppler-XX.XX.X\Library\bin`

## Project Setup Commands

Run these commands in PowerShell or Command Prompt:

```powershell
# Initialize git repository
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: OCR automation service with FastAPI"

# Create GitHub repository first, then connect:
# git remote add origin https://github.com/yourusername/ocr-automation-project.git
# git push -u origin main
```

## Local Development Setup

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the service
python main.py
```

## Docker Setup (Alternative)

If you prefer using Docker:

```powershell
# Build Docker image
docker build -t ocr-service .

# Run container
docker run -p 8000:8000 ocr-service
```

## Verification

1. **Check Git**: `git --version`
2. **Check Python**: `python --version`
3. **Check Tesseract**: `tesseract --version`
4. **Test Service**: Visit `http://localhost:8000/health`

## Troubleshooting

### Git not found
- Restart terminal after Git installation
- Check if Git is in PATH: `echo $env:PATH`

### Python not found
- Reinstall Python with "Add to PATH" checked
- Use `py` instead of `python` on some Windows systems

### Tesseract not found
- Add Tesseract to system PATH
- Restart terminal after PATH changes

### Permission errors
- Run PowerShell as Administrator
- Check file permissions in project folder
