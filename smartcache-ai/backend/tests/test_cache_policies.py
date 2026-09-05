import time
from app.core.models import CacheItem
from app.cache.smart_cache import SmartCache
from app.cache.lru import LRUCache
from app.cache.lfu import LFUCache
from app.cache.gds import GDSFCache


def test_smartcache_vs_lru_cost_retention():
    """
    Validates that SmartCache retains high-cost items that naive LRU evicts
    solely based on recency.
    """
    now = time.time()

    smart = SmartCache(capacity=2)
    lru = LRUCache(capacity=2)

    # Item A is expensive ($0.05, 1000ms latency)
    item_expensive = CacheItem(
        key="expensive_item",
        value="heavy_rec",
        size_bytes=1024,
        retrieval_cost_usd=0.05,
        retrieval_latency_ms=1000.0,
        created_at=now,
        last_accessed_at=now,
        access_count=5
    )

    # Cheap items ($0.001, 10ms latency)
    item_cheap_1 = CacheItem(
        key="cheap_1",
        value="quick_1",
        size_bytes=1024,
        retrieval_cost_usd=0.001,
        retrieval_latency_ms=10.0,
        created_at=now + 1,
        last_accessed_at=now + 1,
        access_count=1
    )
    item_cheap_2 = CacheItem(
        key="cheap_2",
        value="quick_2",
        size_bytes=1024,
        retrieval_cost_usd=0.001,
        retrieval_latency_ms=10.0,
        created_at=now + 2,
        last_accessed_at=now + 2,
        access_count=1
    )

    # Insert into both caches
    for cache in [smart, lru]:
        cache.put(item_expensive, now)
        cache.put(item_cheap_1, now + 1)
        # 3rd item forces eviction on capacity=2
        cache.put(item_cheap_2, now + 2)

    # LRU evicts 'expensive_item' because it was accessed least recently
    assert not lru.contains("expensive_item")
    assert lru.contains("cheap_1")
    assert lru.contains("cheap_2")

    # SmartCache recognizes high retrieval cost and retains 'expensive_item'
    assert smart.contains("expensive_item")
    assert smart.size() == 2


def test_baseline_caches_and_gdsf():
    now = time.time()
    lfu = LFUCache(capacity=2)
    gdsf = GDSFCache(capacity=2)

    item1 = CacheItem(key="k1", value="v1", access_count=10, retrieval_cost_usd=0.01)
    item2 = CacheItem(key="k2", value="v2", access_count=2, retrieval_cost_usd=0.01)
    item3 = CacheItem(key="k3", value="v3", access_count=1, retrieval_cost_usd=0.01)

    for cache in [lfu, gdsf]:
        cache.put(item1, now)
        cache.put(item2, now + 1)
        cache.put(item3, now + 2)

    # Both LFU and GDSF should keep higher frequency/cost items
    assert lfu.contains("k1")
    assert gdsf.contains("k1")
