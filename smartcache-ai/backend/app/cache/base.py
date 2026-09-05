import time
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any
from app.core.models import CacheItem, AlgorithmStats


class BaseCache(ABC):
    def __init__(self, name: str, capacity: int = 100, max_capacity: Optional[int] = None):
        self.name = name
        self.capacity = max_capacity if max_capacity is not None else capacity
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.refreshes = 0
        self.total_cost_saved = 0.0
        self.backend_cost_incurred = 0.0
        self.total_latency_accum_ms = 0.0
        self.cost_weighted_hits_numerator = 0.0
        self.cost_weighted_total_denominator = 0.0

    @abstractmethod
    def get(self, key: str, now: Optional[float] = None) -> Tuple[Optional[Any], bool, float]:
        """Returns (value, is_hit, latency_ms)."""
        pass

    @abstractmethod
    def put(self, item: CacheItem, now: Optional[float] = None) -> Optional[CacheItem]:
        """Puts an item into cache, evicting if necessary. Returns evicted item if any."""
        pass

    @abstractmethod
    def contains(self, key: str) -> bool:
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    def record_request(self, is_hit: bool, cost: float, latency: float):
        if is_hit:
            self.hits += 1
            self.total_cost_saved += cost
            self.cost_weighted_hits_numerator += cost
        else:
            self.misses += 1
            self.backend_cost_incurred += cost

        self.cost_weighted_total_denominator += cost
        self.total_latency_accum_ms += latency

    def get_stats(self) -> AlgorithmStats:
        total = self.hits + self.misses
        hit_ratio = round((self.hits / total * 100.0) if total > 0 else 0.0, 2)

        if self.cost_weighted_total_denominator > 0:
            c_ratio = round(
                (self.cost_weighted_hits_numerator / self.cost_weighted_total_denominator) * 100.0,
                2,
            )
        else:
            c_ratio = hit_ratio

        avg_latency = round(
            (self.total_latency_accum_ms / total) if total > 0 else 0.0,
            2,
        )

        return AlgorithmStats(
            name=self.name,
            hits=self.hits,
            misses=self.misses,
            total_requests=total,
            hit_ratio=hit_ratio,
            cost_weighted_hit_ratio=c_ratio,
            total_cost_saved_usd=round(self.total_cost_saved, 4),
            backend_cost_incurred_usd=round(self.backend_cost_incurred, 4),
            avg_latency_ms=avg_latency,
            evictions=self.evictions,
            refreshes=self.refreshes,
            current_size_items=self.size(),
            max_capacity_items=self.capacity,
        )

    def reset(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.refreshes = 0
        self.total_cost_saved = 0.0
        self.backend_cost_incurred = 0.0
        self.total_latency_accum_ms = 0.0
        self.cost_weighted_hits_numerator = 0.0
        self.cost_weighted_total_denominator = 0.0
