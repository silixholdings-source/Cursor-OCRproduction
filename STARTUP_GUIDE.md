# 🚀 AI ERP SaaS - Complete Startup Guide

## ⚠️ **Current Issue: Partial System Running**

Currently only the web frontend is running. To get the full application working:

## 🔧 **Step 1: Start Docker Desktop**
1. Open Docker Desktop application
2. Wait for it to fully start (Docker icon should be green)
3. Verify with: `docker --version`

## 🚀 **Step 2: Start Full Stack**

### Option A: Full Production Stack
```bash
# From project root
docker-compose up
```

### Option B: Development Stack  
```bash
# From project root
docker-compose -f docker-compose.dev.yml up
```

### Option C: Individual Services (if Docker issues persist)
```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Web Frontend (already running)
cd web
npm run dev

# Terminal 3: Database (requires PostgreSQL installed)
# Setup local PostgreSQL on port 5432
```

## 🌐 **Service Access Points**
- **Web Frontend:** http://localhost:3000 ✅ (Currently Running)
- **Backend API:** http://localhost:8000 ❌ (Not Running)
- **API Docs:** http://localhost:8000/docs ❌ (Not Running)
- **Database:** localhost:5432 ❌ (Not Running)
- **Redis:** localhost:6379 ❌ (Not Running)

## 🧪 **Test Full Functionality**
Once all services are running:

1. **Frontend Tests:**
   - Login with real backend authentication
   - Upload actual invoices for OCR processing
   - Test real approval workflows
   - Verify database persistence

2. **Backend Tests:**
   - API endpoints respond correctly
   - Database operations work
   - File upload and OCR processing
   - User management and permissions

## 🔍 **Troubleshooting**

### Docker Issues:
```bash
# Check Docker status
docker ps

# Stop all containers
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# Start fresh
docker-compose up --force-recreate
```

### Port Conflicts:
```bash
# Check what's using ports
netstat -an | findstr ":3000"
netstat -an | findstr ":8000"
netstat -an | findstr ":5432"
```

### Database Issues:
```bash
# Reset database
docker-compose down -v
docker-compose up
```

## 📋 **Current Status Summary**

| Service | Status | Port | Notes |
|---------|--------|------|-------|
| Web Frontend | ✅ Running | 3000 | Fully functional with mock data |
| Backend API | ❌ Down | 8000 | Needs Docker or manual start |
| PostgreSQL | ❌ Down | 5432 | Needs Docker |
| Redis | ❌ Down | 6379 | Needs Docker |
| Mobile App | ❌ Down | 19000 | Not tested |

## 🎯 **Next Steps**
1. Fix Docker Desktop connection
2. Start full stack with `docker-compose up`
3. Test end-to-end functionality
4. Verify real data persistence
5. Test actual OCR and invoice processing


