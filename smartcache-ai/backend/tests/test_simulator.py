import pytest
from app.core.models import SimulationConfig, WorkloadType, TrafficScenario
from app.simulator.workloads import WorkloadTemplate
from app.simulator.traffic_generator import TrafficGenerator
from app.simulator.benchmark_runner import BenchmarkRunner
from app.api.routes_simulator import start_simulation, step_simulation, get_telemetry, StepRequest


def test_workload_generation():
    read_item = WorkloadTemplate.generate_item("item_1", WorkloadType.READ_HEAVY_API)
    rec_item = WorkloadTemplate.generate_item("item_2", WorkloadType.COMPUTE_HEAVY_RECOMMENDATION)

    assert read_item.key == "item_1"
    assert rec_item.key == "item_2"
    # Recommendation workload has higher retrieval cost & latency than read API
    assert rec_item.retrieval_cost_usd > read_item.retrieval_cost_usd
    assert rec_item.retrieval_latency_ms > read_item.retrieval_latency_ms
    assert rec_item.size_bytes > read_item.size_bytes


def test_traffic_generator_scenarios():
    cfg_steady = SimulationConfig(
        workload_type=WorkloadType.READ_HEAVY_API,
        scenario=TrafficScenario.STEADY_LOAD,
        request_count=80,
        unique_keys=20
    )
    trace_steady = TrafficGenerator.generate_trace(cfg_steady)
    assert len(trace_steady) == 80

    cfg_spike = SimulationConfig(
        workload_type=WorkloadType.COMPUTE_HEAVY_RECOMMENDATION,
        scenario=TrafficScenario.SUDDEN_SPIKE,
        request_count=100,
        unique_keys=25
    )
    trace_spike = TrafficGenerator.generate_trace(cfg_spike)
    assert len(trace_spike) == 100

    cfg_shift = SimulationConfig(
        scenario=TrafficScenario.POPULARITY_SHIFT,
        request_count=120,
        unique_keys=30
    )
    trace_shift = TrafficGenerator.generate_trace(cfg_shift)
    assert len(trace_shift) == 120


def test_benchmark_runner():
    config = SimulationConfig(
        workload_type=WorkloadType.COMPUTE_HEAVY_RECOMMENDATION,
        scenario=TrafficScenario.STEADY_LOAD,
        cache_capacity=25,
        request_count=150,
        unique_keys=50
    )
    result = BenchmarkRunner.run_benchmark(config)
    assert result.request_count == 150
    assert "SmartCache AI" in result.algorithms
    assert "LRU (Baseline)" in result.algorithms
    assert "LFU (Baseline)" in result.algorithms
    assert "GDSF (Baseline)" in result.algorithms

    # All algorithms handled 150 requests
    for name, stats in result.algorithms.items():
        assert stats.total_requests == 150
        assert stats.hits + stats.misses == 150

    assert result.winner is not None
    assert len(result.summary) > 0


def test_simulator_telemetry_flow():
    config = SimulationConfig(
        workload_type=WorkloadType.READ_HEAVY_API,
        scenario=TrafficScenario.STEADY_LOAD,
        cache_capacity=10,
        request_count=40,
        unique_keys=15
    )
    start_resp = start_simulation(config)
    assert start_resp["status"] == "started"

    step_resp = step_simulation(StepRequest(batch_size=15))
    assert step_resp.current_index == 15
    assert step_resp.is_running is True
    assert step_resp.stats.total_requests == 15

    telemetry = get_telemetry()
    assert telemetry.current_index == 15
    assert len(telemetry.adaptive_weights) == 6
