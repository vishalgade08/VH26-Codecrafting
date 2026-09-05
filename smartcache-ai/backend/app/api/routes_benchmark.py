from fastapi import APIRouter
from app.core.models import SimulationConfig, BenchmarkResult
from app.simulator.benchmark_runner import BenchmarkRunner

router = APIRouter(prefix="/api/benchmark", tags=["benchmark"])


@router.post("/run", response_model=BenchmarkResult)
def run_benchmark_endpoint(config: SimulationConfig):
    """Runs fair comparative benchmark of SmartCache AI vs LRU, LFU, and GDSF."""
    result = BenchmarkRunner.run_benchmark(config)
    return result


@router.get("/latest", response_model=BenchmarkResult)
def get_latest_benchmark():
    """Retrieves the latest benchmark result or generates one on default configuration."""
    if BenchmarkRunner.latest_result is not None:
        return BenchmarkRunner.latest_result
    # Run default benchmark if none available
    default_config = SimulationConfig()
    return BenchmarkRunner.run_benchmark(default_config)
