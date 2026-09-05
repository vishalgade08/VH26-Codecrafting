import time
from typing import Optional, Tuple, Any, Dict
from app.cache.base import BaseCache
from app.core.models import CacheItem
from app.core.config import settings


class GDSFCache(BaseCache):
    """
    GreedyDual-Size Frequency (GDSF) algorithm:
    H_i = L + F_i * (Cost_i / Size_i)
    L is an aging factor updated to the evicted item's H value.
    """

    def __init__(self, capacity: int = 100, max_capacity: Optional[int] = None):
        super().__init__(name="GreedyDual-Size (GDSF)", capacity=capacity, max_capacity=max_capacity)
        self.cache: Dict[str, CacheItem] = {}
        self.h_values: Dict[str, float] = {}
        self.clock_l: float = 0.0

    def _calc_h(self, item: CacheItem) -> float:
        size_kb = max(item.size_bytes / 1024.0, 0.1)
        cost_metric = item.retrieval_cost_usd * 1000.0
        return self.clock_l + (item.access_count * (cost_metric / size_kb))

    def get(self, key: str, now: Optional[float] = None) -> Tuple[Optional[Any], bool, float]:
        if now is None:
            now = time.time()
        if key in self.cache:
            item = self.cache[key]
            item.last_accessed_at = now
            item.access_count += 1
            self.h_values[key] = self._calc_h(item)
            latency = settings.costs.base_cache_latency_ms
            self.record_request(is_hit=True, cost=item.retrieval_cost_usd, latency=latency)
            return item.value, True, latency
        return None, False, 0.0

    def put(self, item: CacheItem, now: Optional[float] = None) -> Optional[CacheItem]:
        if now is None:
            now = time.time()
        item.last_accessed_at = now
        evicted = None
        if item.key in self.cache:
            self.cache[item.key].value = item.value
            self.cache[item.key].access_count += 1
            self.cache[item.key].last_accessed_at = now
            self.h_values[item.key] = self._calc_h(self.cache[item.key])
        else:
            if len(self.cache) >= self.capacity:
                victim_key = min(self.cache.keys(), key=lambda k: self.h_values.get(k, 0.0))
                self.clock_l = self.h_values.get(victim_key, 0.0)
                evicted = self.cache.pop(victim_key)
                self.h_values.pop(victim_key, None)
                self.evictions += 1
            self.cache[item.key] = item
            self.h_values[item.key] = self._calc_h(item)
        return evicted

    def contains(self, key: str) -> bool:
        return key in self.cache

    def size(self) -> int:
        return len(self.cache)

    def reset(self):
        super().reset()
        self.cache.clear()
        self.h_values.clear()
        self.clock_l = 0.0
