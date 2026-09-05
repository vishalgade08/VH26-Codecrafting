import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.routes_cache import router as cache_router
from app.api.routes_benchmark import router as benchmark_router
from app.api.routes_simulator import router as simulator_router

load_dotenv()

app = FastAPI(
    title="SmartCache AI Backend",
    description="Adaptive Application-Aware Cache Management System with Multi-Factor Scoring",
    version="1.0.0"
)

cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "SmartCache AI Backend",
        "status": "online",
        "documentation": "/docs",
        "frontend_dashboard": "http://localhost:5173",
        "health_check": "/api/health"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "SmartCache AI Backend"
    }


# Mount Routers
app.include_router(cache_router)
app.include_router(benchmark_router)
app.include_router(simulator_router)


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
