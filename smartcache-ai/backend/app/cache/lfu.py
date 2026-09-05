import time
from typing import Optional, Tuple, Any, Dict
from app.cache.base import BaseCache
from app.core.models import CacheItem
from app.core.config import settings


class LFUCache(BaseCache):
    def __init__(self, capacity: int = 100, max_capacity: Optional[int] = None):
        super().__init__(name="Standard LFU", capacity=capacity, max_capacity=max_capacity)
        self.cache: Dict[str, CacheItem] = {}

    def get(self, key: str, now: Optional[float] = None) -> Tuple[Optional[Any], bool, float]:
        if now is None:
            now = time.time()
        if key in self.cache:
            item = self.cache[key]
            item.last_accessed_at = now
            item.access_count += 1
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
        else:
            if len(self.cache) >= self.capacity:
                min_key = min(
                    self.cache.keys(),
                    key=lambda k: (self.cache[k].access_count, self.cache[k].last_accessed_at),
                )
                evicted = self.cache.pop(min_key)
                self.evictions += 1
            self.cache[item.key] = item
        return evicted

    def contains(self, key: str) -> bool:
        return key in self.cache

    def size(self) -> int:
        return len(self.cache)

    def reset(self):
        super().reset()
        self.cache.clear()
