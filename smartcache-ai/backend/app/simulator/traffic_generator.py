import random
import math
from typing import List, Dict
from app.core.models import SimulationConfig, TrafficScenario, CacheItem
from app.simulator.workloads import WorkloadTemplate


class TrafficGenerator:
    """Generates synthetic multi-pattern traffic traces simulating real production workloads."""

    @staticmethod
    def create_item_pool(config: SimulationConfig) -> Dict[str, CacheItem]:
        """Creates a pool of consistent items with their realistic cost/latency profiles."""
        pool: Dict[str, CacheItem] = {}
        for i in range(config.unique_keys):
            key = f"key_{i:04d}"
            # Items have realistic application cost and latency attributes
            item = WorkloadTemplate.generate_item(key, config.workload_type)
            # 10% of items are expensive compute tasks (e.g. complex queries or aggregations)
            if i % 10 == 0:
                item.retrieval_cost_usd *= 4.5
                item.retrieval_latency_ms *= 3.0
            pool[key] = item
        return pool

    @classmethod
    def generate_trace(cls, config: SimulationConfig) -> List[str]:
        """Generates a sequence of cache key requests based on the selected traffic scenario."""
        keys = [f"key_{i:04d}" for i in range(config.unique_keys)]
        n_req = config.request_count

        if config.scenario == TrafficScenario.STEADY_LOAD:
            return cls._generate_steady_zipf(keys, n_req, alpha=1.15)
        elif config.scenario == TrafficScenario.SUDDEN_SPIKE:
            return cls._generate_spike(keys, n_req, config.spike_multiplier)
        elif config.scenario == TrafficScenario.POPULARITY_SHIFT:
            return cls._generate_popularity_shift(keys, n_req)
        else:
            return cls._generate_steady_zipf(keys, n_req, alpha=1.1)

    @staticmethod
    def _generate_steady_zipf(keys: List[str], count: int, alpha: float = 1.15) -> List[str]:
        """Zipfian distribution where top rank keys dominate."""
        weights = [1.0 / math.pow(rank + 1, alpha) for rank in range(len(keys))]
        return random.choices(keys, weights=weights, k=count)

    @staticmethod
    def _generate_spike(keys: List[str], count: int, multiplier: float) -> List[str]:
        """Baseline traffic followed by an intense burst on a viral cluster of keys."""
        p1_len = int(count * 0.30)
        p2_len = int(count * 0.40)
        p3_len = count - p1_len - p2_len

        # Viral keys (e.g., breaking news, viral product)
        start_idx = int(len(keys) * 0.4)
        viral_keys = keys[start_idx:start_idx + 6]
        if not viral_keys:
            viral_keys = keys[:5]

        # Phase 1: Baseline Zipf
        p1 = TrafficGenerator._generate_steady_zipf(keys, p1_len, alpha=1.1)

        # Phase 2: Spike - 75% traffic concentrated on viral keys
        p2 = []
        for _ in range(p2_len):
            if random.random() < 0.75:
                p2.append(random.choice(viral_keys))
            else:
                p2.append(random.choice(keys))

        # Phase 3: Gradual recovery
        p3 = TrafficGenerator._generate_steady_zipf(keys, p3_len, alpha=1.1)

        return p1 + p2 + p3

    @staticmethod
    def _generate_popularity_shift(keys: List[str], count: int) -> List[str]:
        """Shift in popular items over time (early items cool off, new items trend)."""
        half_keys = len(keys) // 2
        keys_early = keys[:half_keys] if half_keys > 0 else keys
        keys_late = keys[half_keys:] if half_keys > 0 else keys

        half_count = count // 2
        rem_count = count - half_count

        # Early phase: top half of keys popular
        p1 = TrafficGenerator._generate_steady_zipf(keys_early, half_count, alpha=1.2)
        # Late phase: bottom half of keys trending
        p2 = TrafficGenerator._generate_steady_zipf(keys_late, rem_count, alpha=1.2)

        return p1 + p2
