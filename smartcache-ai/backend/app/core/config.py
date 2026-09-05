import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class CostModelConfig(BaseModel):
    # Costs in USD
    cost_per_api_call: float = float(os.getenv("COST_PER_API_CALL", "0.005"))
    cost_per_compute_second: float = float(os.getenv("COST_PER_COMPUTE_SEC", "0.00004"))
    cost_per_mb_hour_ram: float = float(os.getenv("COST_PER_MB_HOUR_RAM", "0.000015"))
    # Base network latency overhead in ms
    base_cache_latency_ms: float = float(os.getenv("BASE_CACHE_LATENCY_MS", "1.2"))


class Settings(BaseModel):
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    environment: str = os.getenv("ENVIRONMENT", "development")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    database_url: str = os.getenv("DATABASE_URL", "postgresql://smartcache_user:smartcache_password@localhost:5432/smartcache")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    costs: CostModelConfig = CostModelConfig()


settings = Settings()
