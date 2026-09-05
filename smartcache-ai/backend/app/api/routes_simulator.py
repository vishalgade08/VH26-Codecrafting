import time
from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.models import SimulationConfig, WorkloadType, TrafficScenario, AlgorithmStats, DecisionEvent
from app.core.config import settings
from app.cache.smart_cache import SmartCache
from app.simulator.traffic_generator import TrafficGenerator

router = APIRouter(prefix="/api/simulator", tags=["simulator"])


class SimulatorState:
    is_running: bool = False
    config: SimulationConfig = SimulationConfig()
    cache: SmartCache = SmartCache(capacity=50)
    pool: Dict[str, Any] = {}
    trace: List[str] = []
    current_index: int = 0
    sim_time: float = 0.0


state = SimulatorState()


class StepRequest(BaseModel):
    batch_size: int = 15


class TelemetryResponse(BaseModel):
    is_running: bool
    workload: str
    scenario: str
    current_index: int
    total_steps: int
    progress_pct: float
    stats: AlgorithmStats
    recent_decisions: List[DecisionEvent]
    adaptive_weights: Dict[str, float]
    memory_pressure_pct: float


@router.post("/start")
def start_simulation(config: SimulationConfig):
    """Initializes and starts a new dynamic simulation session."""
    state.config = config
    state.cache = SmartCache(capacity=config.cache_capacity)
    state.pool = TrafficGenerator.create_item_pool(config)
    state.trace = TrafficGenerator.generate_trace(config)
    state.current_index = 0
    state.sim_time = time.time()
    state.is_running = True

    return {
        "status": "started",
        "workload": config.workload_type.value,
        "scenario": config.scenario.value,
        "capacity": config.cache_capacity,
        "total_requests": len(state.trace)
    }


@router.post("/step", response_model=TelemetryResponse)
def step_simulation(req: StepRequest = StepRequest()):
    """Advances the simulation by batch_size requests, recording real-time decisions."""
    if not state.trace:
        start_simulation(state.config)

    end_index = min(state.current_index + req.batch_size, len(state.trace))
    for i in range(state.current_index, end_index):
        state.sim_time += 0.05
        key = state.trace[i]
        item = state.pool.get(key)
        if item is not None:
            val, is_hit, _ = state.cache.get(key, state.sim_time)
            if not is_hit:
                miss_lat = item.retrieval_latency_ms + settings.costs.base_cache_latency_ms
                state.cache.record_request(is_hit=False, cost=item.retrieval_cost_usd, latency=miss_lat)
                state.cache.put(item.model_copy(deep=True), state.sim_time)

    state.current_index = end_index
    if state.current_index >= len(state.trace):
        state.is_running = False

    return get_telemetry()


@router.get("/telemetry", response_model=TelemetryResponse)
def get_telemetry():
    """Fetches real-time cache metrics, weights, and decisions for the dashboard."""
    stats = state.cache.get_stats()
    decisions = state.cache.get_recent_decisions(limit=25)
    weights = state.cache.scorer.weights
    total = len(state.trace) if state.trace else 1
    progress = round((state.current_index / total) * 100, 1)
    pressure = round((stats.current_size_items / max(stats.max_capacity_items, 1)) * 100, 1)

    return TelemetryResponse(
        is_running=state.is_running,
        workload=state.config.workload_type.value,
        scenario=state.config.scenario.value,
        current_index=state.current_index,
        total_steps=len(state.trace),
        progress_pct=progress,
        stats=stats,
        recent_decisions=decisions,
        adaptive_weights=weights,
        memory_pressure_pct=pressure
    )


@router.post("/stop")
def stop_simulation():
    """Pauses or stops the active simulation."""
    state.is_running = False
    return {"status": "stopped", "current_index": state.current_index}
