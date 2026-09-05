import time
from collections import OrderedDict
from typing import Optional, Tuple, Any
from app.cache.base import BaseCache
from app.core.models import CacheItem
from app.core.config import settings


class LRUCache(BaseCache):
    def __init__(self, capacity: int = 100, max_capacity: Optional[int] = None):
        super().__init__(name="Standard LRU", capacity=capacity, max_capacity=max_capacity)
        self.cache: OrderedDict[str, CacheItem] = OrderedDict()

    def get(self, key: str, now: Optional[float] = None) -> Tuple[Optional[Any], bool, float]:
        if now is None:
            now = time.time()
        if key in self.cache:
            item = self.cache[key]
            item.last_accessed_at = now
            item.access_count += 1
            self.cache.move_to_end(key)
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
            self.cache.move_to_end(item.key)
            self.cache[item.key] = item
        else:
            if len(self.cache) >= self.capacity:
                evicted_key, evicted = self.cache.popitem(last=False)
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
