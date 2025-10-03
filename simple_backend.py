from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="AI ERP API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI ERP API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "API is running"}

@app.get("/api/v1/health")
async def api_health():
    return {"status": "healthy", "message": "API v1 is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)