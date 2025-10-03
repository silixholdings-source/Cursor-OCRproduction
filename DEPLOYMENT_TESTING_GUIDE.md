# 🧪 OCR Service Deployment Testing Guide

This guide shows you how to test your deployed OCR automation service on Render.

## 🚀 Quick Test Methods

### 1. **Browser Testing (Easiest)**

Once your service is deployed, you can test it directly in your browser:

#### Health Check
```
https://your-service-name.onrender.com/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "service": "OCR Automation Service",
  "version": "1.0.0",
  "provider": "tesseract"
}
```

#### API Documentation
```
https://your-service-name.onrender.com/docs
```
This opens the interactive Swagger UI where you can test all endpoints.

#### Service Information
```
https://your-service-name.onrender.com/
```
**Expected Response:**
```json
{
  "service": "OCR Automation Service",
  "version": "1.0.0",
  "status": "running",
  "provider": "tesseract",
  "endpoints": {
    "health": "/health",
    "ready": "/ready",
    "ocr": "/ocr",
    "docs": "/docs"
  }
}
```

### 2. **Command Line Testing**

#### Using curl (if available)
```bash
# Health check
curl https://your-service-name.onrender.com/health

# Service info
curl https://your-service-name.onrender.com/

# Readiness check
curl https://your-service-name.onrender.com/ready
```

#### Using PowerShell (Windows)
```powershell
# Health check
Invoke-WebRequest -Uri "https://your-service-name.onrender.com/health" -Method GET

# Service info
Invoke-WebRequest -Uri "https://your-service-name.onrender.com/" -Method GET
```

### 3. **Python Testing Script**

Run the comprehensive test script:

```bash
python test_deployment.py
```

The script will:
- ✅ Test all endpoints
- ✅ Verify service health
- ✅ Check API documentation
- ✅ Optionally test file upload

### 4. **Interactive API Testing**

1. Go to `https://your-service-name.onrender.com/docs`
2. Click on the `/ocr` endpoint
3. Click "Try it out"
4. Upload a test image or PDF
5. Click "Execute"

## 📊 Testing Checklist

### ✅ **Basic Connectivity**
- [ ] Service responds to health check
- [ ] Service returns correct status
- [ ] API documentation is accessible
- [ ] All endpoints are listed correctly

### ✅ **OCR Functionality**
- [ ] Can upload image files (JPG, PNG)
- [ ] Can upload PDF files
- [ ] Returns extracted text
- [ ] Provides confidence scores
- [ ] Handles errors gracefully

### ✅ **Performance**
- [ ] Service starts within reasonable time
- [ ] OCR processing completes in under 30 seconds
- [ ] Service doesn't timeout on large files
- [ ] Memory usage is reasonable

## 🔧 **Test Files**

Create test files to verify OCR functionality:

### Sample Images
- Screenshot of text document
- Photo of printed text
- Scanned document image

### Sample PDFs
- Text-based PDF (should work well)
- Image-based PDF (may need OCR)

## 🚨 **Common Issues & Solutions**

### Issue: Service Not Responding
**Symptoms:** Timeout errors, 502/503 errors
**Solutions:**
- Check Render dashboard for deployment status
- Verify environment variables are set
- Check build logs for errors

### Issue: OCR Not Working
**Symptoms:** Empty text returned, low confidence scores
**Solutions:**
- Ensure Tesseract is properly installed in Docker
- Check image quality and format
- Verify file size limits

### Issue: Slow Performance
**Symptoms:** Long response times, timeouts
**Solutions:**
- Check Render service logs
- Consider upgrading Render plan
- Optimize image file sizes

## 📈 **Performance Benchmarks**

### Expected Response Times:
- **Health Check:** < 1 second
- **Simple OCR:** 2-5 seconds
- **Complex PDF:** 10-30 seconds

### File Size Limits:
- **Images:** Up to 10MB
- **PDFs:** Up to 10MB
- **Supported Formats:** JPG, PNG, PDF, TIFF

## 🎯 **Success Criteria**

Your deployment is successful if:
1. ✅ All endpoints respond correctly
2. ✅ OCR extracts text from test images
3. ✅ Service handles errors gracefully
4. ✅ API documentation is accessible
5. ✅ Performance meets expectations

## 🔄 **Continuous Testing**

Set up automated testing:
1. Use GitHub Actions to test on each deployment
2. Monitor service health with uptime checks
3. Set up alerts for service failures
4. Regular performance testing

## 📞 **Getting Help**

If you encounter issues:
1. Check Render service logs
2. Review GitHub Actions workflow
3. Test locally first
4. Verify environment configuration

---

**Happy Testing! 🎉**

Your OCR automation service should be fully functional once deployed. The comprehensive test script will help you verify all functionality works as expected.
