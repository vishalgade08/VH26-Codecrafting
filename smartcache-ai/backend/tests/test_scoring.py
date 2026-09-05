import time
from app.core.models import CacheItem, DecisionAction
from app.cache.scoring import DynamicScorer


def test_scorer_factors_and_decision():
    scorer = DynamicScorer()
    now = time.time()

    item = CacheItem(
        key="test_item_high",
        value={"data": "val"},
        size_bytes=1024,
        retrieval_cost_usd=0.045,
        retrieval_latency_ms=800.0,
        created_at=now - 10.0,
        last_accessed_at=now,
        access_count=20,
        ttl_seconds=300.0
    )

    breakdown = scorer.score_item(item, now)
    assert breakdown.final_score >= 70.0
    assert breakdown.decision in [DecisionAction.RETAIN, DecisionAction.MONITOR]
    assert breakdown.retrieval_cost >= 80.0


def test_stale_refresh_decision():
    scorer = DynamicScorer()
    now = time.time()

    item = CacheItem(
        key="stale_valuable",
        value={"data": "important"},
        size_bytes=2048,
        retrieval_cost_usd=0.040,
        retrieval_latency_ms=900.0,
        created_at=now - 400.0,
        last_accessed_at=now,
        access_count=30,
        ttl_seconds=300.0,
        is_stale=True
    )

    breakdown = scorer.score_item(item, now)
    assert breakdown.decision == DecisionAction.REFRESH


def test_adaptive_weights_under_pressure():
    scorer = DynamicScorer()

    w_default = scorer.get_adaptive_weights(memory_pressure_ratio=0.5, db_pressure_ratio=0.5)

    # Under memory pressure, size_efficiency should be prioritized
    w_mem = scorer.get_adaptive_weights(memory_pressure_ratio=0.9, db_pressure_ratio=0.5)
    assert w_mem["size_efficiency"] > w_default["size_efficiency"]

    # Under DB pressure, retrieval_cost should be prioritized
    w_db = scorer.get_adaptive_weights(memory_pressure_ratio=0.5, db_pressure_ratio=0.9)
    assert w_db["retrieval_cost"] > w_default["retrieval_cost"]
