import time
from typing import Dict, Optional
from app.core.models import SimulationConfig, BenchmarkResult, AlgorithmStats
from app.core.config import settings
from app.simulator.traffic_generator import TrafficGenerator
from app.cache.smart_cache import SmartCache
from app.cache.lru import LRUCache
from app.cache.lfu import LFUCache
from app.cache.gds import GDSFCache


class BenchmarkRunner:
    """Executes fair comparative benchmarks across SmartCache, LRU, LFU, and GDSF on identical traces."""

    latest_result: Optional[BenchmarkResult] = None

    @classmethod
    def run_benchmark(cls, config: SimulationConfig) -> BenchmarkResult:
        start_time = time.time()

        pool = TrafficGenerator.create_item_pool(config)
        trace = TrafficGenerator.generate_trace(config)

        # Initialize all 4 cache implementations with identical capacity
        caches = {
            "SmartCache AI": SmartCache(capacity=config.cache_capacity),
            "LRU (Baseline)": LRUCache(capacity=config.cache_capacity),
            "LFU (Baseline)": LFUCache(capacity=config.cache_capacity),
            "GDSF (Baseline)": GDSFCache(capacity=config.cache_capacity),
        }

        # Run identical requests through each algorithm
        now = time.time()
        for name, cache in caches.items():
            t = now
            for key in trace:
                t += 0.05
                item = pool[key]
                val, is_hit, _ = cache.get(key, t)
                if not is_hit:
                    # Cache miss: fetch from backend, incurring backend latency + cost
                    miss_lat = item.retrieval_latency_ms + settings.costs.base_cache_latency_ms
                    cache.record_request(is_hit=False, cost=item.retrieval_cost_usd, latency=miss_lat)
                    cache.put(item.model_copy(deep=True), t)

        duration = time.time() - start_time

        # Extract stats
        stats_map: Dict[str, AlgorithmStats] = {
            name: cache.get_stats() for name, cache in caches.items()
        }

        smart_stats = stats_map["SmartCache AI"]
        lru_stats = stats_map["LRU (Baseline)"]

        # Calculate cost savings delta vs baseline LRU
        if lru_stats.total_cost_saved_usd > 0:
            diff_pct = round(
                ((smart_stats.total_cost_saved_usd - lru_stats.total_cost_saved_usd) / lru_stats.total_cost_saved_usd) * 100,
                2
            )
        else:
            diff_pct = 0.0

        # Determine winner based on cost-weighted efficiency
        winner = max(stats_map.items(), key=lambda x: (x[1].total_cost_saved_usd, x[1].cost_weighted_hit_ratio))[0]

        summary = (
            f"SmartCache AI saved ${smart_stats.total_cost_saved_usd:.4f} "
            f"({diff_pct:+.1f}% vs LRU) with a {smart_stats.cost_weighted_hit_ratio:.1f}% "
            f"cost-weighted hit rate across {len(trace)} requests in {config.scenario.value}."
        )

        result = BenchmarkResult(
            workload=config.workload_type.value,
            scenario=config.scenario.value,
            request_count=len(trace),
            duration_seconds=round(duration, 3),
            algorithms=stats_map,
            winner=winner,
            cost_savings_diff_vs_lru_pct=diff_pct,
            summary=summary
        )

        cls.latest_result = result
        return result
