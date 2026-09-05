import time
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DecisionAction(str, Enum):
    RETAIN = "RETAIN"
    MONITOR = "MONITOR"
    EVICT = "EVICT"
    REFRESH = "REFRESH"


class ScoreBreakdown(BaseModel):
    frequency: float = 0.0
    recency: float = 0.0
    retrieval_cost: float = 0.0
    latency: float = 0.0
    popularity: float = 0.0
    size_efficiency: float = 0.0
    final_score: float = 0.0
    decision: DecisionAction = DecisionAction.MONITOR
    weights: Dict[str, float] = Field(default_factory=dict)
    justification: str = ""


class CacheItem(BaseModel):
    key: str
    value: Any
    size_bytes: int = 1024
    retrieval_cost_usd: float = 0.005
    retrieval_latency_ms: float = 50.0
    created_at: float = Field(default_factory=time.time)
    last_accessed_at: float = Field(default_factory=time.time)
    access_count: int = 1
    ttl_seconds: float = 300.0
    is_stale: bool = False
    current_score: float = 0.0
    score_breakdown: Optional[ScoreBreakdown] = None


class DecisionEvent(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    key: str
    action: DecisionAction
    score: float
    justification: str
    factors: Dict[str, float]


class AlgorithmStats(BaseModel):
    name: str
    hits: int = 0
    misses: int = 0
    total_requests: int = 0
    hit_ratio: float = 0.0
    cost_weighted_hit_ratio: float = 0.0
    total_cost_saved_usd: float = 0.0
    backend_cost_incurred_usd: float = 0.0
    avg_latency_ms: float = 0.0
    evictions: int = 0
    refreshes: int = 0
    current_size_items: int = 0
    max_capacity_items: int = 100


class CachePutRequest(BaseModel):
    key: str
    value: Any
    size_bytes: int = 1024
    retrieval_cost_usd: float = 0.005
    retrieval_latency_ms: float = 50.0
    ttl_seconds: float = 300.0


class ScalingEvaluation(BaseModel):
    recommendation: str
    reason: str
    roi_ratio: float
    monthly_savings_proj_usd: float
    monthly_capacity_cost_usd: float
    suggested_capacity: int
    current_capacity: int
    current_hit_rate_pct: float


class WorkloadType(str, Enum):
    READ_HEAVY_API = "READ_HEAVY_API"
    COMPUTE_HEAVY_RECOMMENDATION = "COMPUTE_HEAVY_RECOMMENDATION"


class TrafficScenario(str, Enum):
    STEADY_LOAD = "STEADY_LOAD"
    SUDDEN_SPIKE = "SUDDEN_SPIKE"
    POPULARITY_SHIFT = "POPULARITY_SHIFT"


class SimulationConfig(BaseModel):
    workload_type: WorkloadType = WorkloadType.READ_HEAVY_API
    scenario: TrafficScenario = TrafficScenario.STEADY_LOAD
    cache_capacity: int = 50
    request_count: int = 500
    unique_keys: int = 150
    spike_multiplier: float = 3.0


class BenchmarkResult(BaseModel):
    workload: str
    scenario: str
    request_count: int
    duration_seconds: float
    algorithms: Dict[str, AlgorithmStats]
    winner: str
    cost_savings_diff_vs_lru_pct: float = 0.0
    summary: str
