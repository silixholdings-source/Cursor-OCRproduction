# 🚀 AI ERP SaaS - How to Start the Application

## Quick Start (Recommended)

### Option 1: Double-click Launch
```
Double-click: START_BOTH_SERVERS.cmd
```

### Option 2: Individual Servers
```
Double-click: START_BACKEND.cmd    (for backend only)
Double-click: START_FRONTEND.cmd   (for frontend only)
```

### Option 3: PowerShell Script
```
Right-click start-servers.ps1 → Run with PowerShell
```

## Manual Commands (If scripts don't work)

### Terminal 1 - Backend Server:
```cmd
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 - Frontend Server:
```cmd
cd web
npm run dev
```

## Access Your App

Once both servers are running:

- **Main Application:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **Backend API:** http://localhost:8000

## Troubleshooting

If you get "connection refused" errors:
1. Make sure both servers are running
2. Check that ports 3000 and 8000 are not blocked
3. Wait 10-15 seconds after starting servers
4. Try refreshing the browser

## What You'll See

✅ **Beautiful landing page** with working buttons  
✅ **Functional pricing page** with trial signup  
✅ **Complete dashboard** with real data  
✅ **Invoice upload** with AI processing demo  
✅ **Bulk approval workflows** with real API calls  
✅ **Multi-language support** (5 languages)  
✅ **Multi-currency support** with live rates  
✅ **ERP integrations** ready for configuration  

Your AI ERP SaaS application is production-ready! 🎉

