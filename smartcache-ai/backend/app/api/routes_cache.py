import time
from fastapi import APIRouter, Query, HTTPException
from app.cache.smart_cache import SmartCache
from app.core.models import CachePutRequest, CacheItem, AlgorithmStats, ScalingEvaluation
from app.cache.scoring import scorer

router = APIRouter(prefix="/api/cache", tags=["Cache"])

# Primary SmartCache instance
cache_engine = SmartCache(capacity=50)


@router.get("/stats", response_model=AlgorithmStats)
def get_cache_stats():
    return cache_engine.get_stats()


@router.get("/decisions")
def get_decisions(limit: int = Query(25, ge=1, le=100)):
    return cache_engine.get_recent_decisions(limit=limit)


@router.get("/scaling-analysis", response_model=ScalingEvaluation)
def get_scaling_analysis():
    return cache_engine.evaluate_scaling()


@router.post("/put")
def put_item(req: CachePutRequest):
    now = time.time()
    item = CacheItem(
        key=req.key,
        value=req.value,
        size_bytes=req.size_bytes,
        retrieval_cost_usd=req.retrieval_cost_usd,
        retrieval_latency_ms=req.retrieval_latency_ms,
        ttl_seconds=req.ttl_seconds,
        created_at=now,
        last_accessed_at=now,
        access_count=1
    )
    evicted = cache_engine.put(item, now)
    return {
        "status": "cached",
        "key": req.key,
        "score": item.current_score,
        "decision": item.score_breakdown.decision if item.score_breakdown else "MONITOR",
        "evicted": evicted.key if evicted else None
    }


@router.get("/get/{key}")
def get_item(key: str):
    now = time.time()
    val, is_hit, lat = cache_engine.get(key, now)
    if not is_hit:
        return {
            "hit": False,
            "key": key,
            "value": None,
            "latency_ms": lat,
            "message": "Cache miss. Data must be regenerated from source backend."
        }

    item = cache_engine.cache[key]
    return {
        "hit": True,
        "key": key,
        "value": val,
        "latency_ms": lat,
        "score": item.current_score,
        "score_breakdown": item.score_breakdown
    }


@router.post("/reset")
def reset_cache():
    cache_engine.reset()
    return {"message": "Cache engine reset successfully"}
