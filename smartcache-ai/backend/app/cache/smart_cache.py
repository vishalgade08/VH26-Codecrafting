import time
from typing import Optional, Tuple, Any, Dict, List
from collections import deque
from app.cache.base import BaseCache
from app.core.models import CacheItem, DecisionAction, DecisionEvent, ScoreBreakdown, ScalingEvaluation
from app.cache.scoring import scorer
from app.core.config import settings


class SmartCache(BaseCache):
    """
    Adaptive Application-Aware Cache Management System.
    Uses multi-factor scoring (Frequency, Recency, Retrieval Cost, Latency,
    Popularity Trend, Size Efficiency) and dynamic weights to optimize
    cost-weighted hit rate and infrastructure spend.
    """

    def __init__(self, capacity: int = 100, max_capacity: Optional[int] = None):
        super().__init__(name="SmartCache AI", capacity=capacity, max_capacity=max_capacity)
        self.cache: Dict[str, CacheItem] = {}
        self.decision_history: deque[DecisionEvent] = deque(maxlen=200)
        self.refresh_queue: deque[str] = deque()
        self.total_backend_calls_avoided = 0
        self.system_memory_pressure = 0.5
        self.system_db_pressure = 0.5
        self.system_traffic_burst = 0.5

    @property
    def scorer(self):
        return scorer

    def get(self, key: str, now: Optional[float] = None) -> Tuple[Optional[Any], bool, float]:
        if now is None:
            now = time.time()

        if key in self.cache:
            item = self.cache[key]
            item.last_accessed_at = now
            item.access_count += 1

            is_stale = item.is_stale or ((now - item.created_at) > item.ttl_seconds)

            breakdown = scorer.score_item(
                item,
                now,
                memory_pressure=self.system_memory_pressure,
                db_pressure=self.system_db_pressure,
                traffic_burst=self.system_traffic_burst,
            )

            if is_stale and breakdown.decision == DecisionAction.REFRESH:
                self.refreshes += 1
                item.created_at = now
                item.is_stale = False
                self._log_decision(key, DecisionAction.REFRESH, breakdown.final_score, breakdown.justification, breakdown)

            latency = settings.costs.base_cache_latency_ms
            self.total_backend_calls_avoided += 1
            self.record_request(is_hit=True, cost=item.retrieval_cost_usd, latency=latency)
            return item.value, True, latency

        return None, False, 0.0

    def put(self, item: CacheItem, now: Optional[float] = None) -> Optional[CacheItem]:
        if now is None:
            now = time.time()

        item.last_accessed_at = now
        evicted = None

        breakdown = scorer.score_item(
            item,
            now,
            memory_pressure=self.system_memory_pressure,
            db_pressure=self.system_db_pressure,
            traffic_burst=self.system_traffic_burst,
        )

        if item.key in self.cache:
            existing = self.cache[item.key]
            existing.value = item.value
            existing.last_accessed_at = now
            existing.access_count += 1
            existing.created_at = now
            existing.is_stale = False
            scorer.score_item(existing, now)
            self._log_decision(item.key, DecisionAction.RETAIN, existing.current_score, "Cache entry updated", breakdown)
        else:
            if len(self.cache) >= self.capacity:
                evicted = self._evict_least_valuable(now)

            self.cache[item.key] = item
            self._log_decision(item.key, breakdown.decision, breakdown.final_score, breakdown.justification, breakdown)

        return evicted

    def _evict_least_valuable(self, now: float) -> Optional[CacheItem]:
        if not self.cache:
            return None

        for item in self.cache.values():
            scorer.score_item(
                item,
                now,
                memory_pressure=self.system_memory_pressure,
                db_pressure=self.system_db_pressure,
                traffic_burst=self.system_traffic_burst,
            )

        victim_key = min(self.cache.keys(), key=lambda k: self.cache[k].current_score)
        evicted_item = self.cache.pop(victim_key)
        self.evictions += 1

        if evicted_item.score_breakdown:
            self._log_decision(
                victim_key,
                DecisionAction.EVICT,
                evicted_item.current_score,
                f"Evicted lowest value item (score: {evicted_item.current_score:.1f})",
                evicted_item.score_breakdown,
            )
        return evicted_item

    def _log_decision(
        self,
        key: str,
        action: DecisionAction,
        score: float,
        justification: str,
        breakdown: ScoreBreakdown,
    ):
        factors = {
            "frequency": breakdown.frequency,
            "recency": breakdown.recency,
            "retrieval_cost": breakdown.retrieval_cost,
            "latency": breakdown.latency,
            "popularity": breakdown.popularity,
            "size_efficiency": breakdown.size_efficiency,
        }
        event = DecisionEvent(
            timestamp=time.time(),
            key=key,
            action=action,
            score=round(score, 1),
            justification=justification,
            factors=factors,
        )
        self.decision_history.appendleft(event)

    def get_recent_decisions(self, limit: int = 25) -> List[DecisionEvent]:
        return list(self.decision_history)[:limit]

    def contains(self, key: str) -> bool:
        return key in self.cache

    def size(self) -> int:
        return len(self.cache)

    def reset(self):
        super().reset()
        self.cache.clear()
        self.decision_history.clear()
        self.refresh_queue.clear()
        self.total_backend_calls_avoided = 0

    def evaluate_scaling(self) -> ScalingEvaluation:
        stats = self.get_stats()
        utilization = self.size() / max(self.capacity, 1)

        # Baseline cost per cache slot: ~$0.00008 per slot/day in RAM equivalent
        monthly_ram_cost_per_slot = 0.05
        current_monthly_ram_cost = round(self.capacity * monthly_ram_cost_per_slot, 2)

        # Extrapolate monthly savings: (total_cost_saved / requests) * est_monthly_requests
        total_reqs = max(stats.total_requests, 1)
        savings_per_req = stats.total_cost_saved_usd / total_reqs
        est_monthly_reqs = 500000
        monthly_savings_proj = round(savings_per_req * est_monthly_reqs, 2)

        roi = round(monthly_savings_proj / max(current_monthly_ram_cost, 0.01), 2)

        if utilization > 0.85 and stats.evictions > 10:
            suggested = int(self.capacity * 1.5)
            rec = "SCALE_UP"
            reason = f"High capacity pressure ({utilization*100:.0f}%) and frequent evictions ({stats.evictions}). Increasing cache size by 50% will reduce expensive backend regeneration."
        elif utilization < 0.30 and self.capacity > 50:
            suggested = max(int(self.capacity * 0.7), 20)
            rec = "SCALE_DOWN"
            reason = f"Low cache utilization ({utilization*100:.0f}%). Scaling down will conserve operational memory overhead without degrading hit rates."
        else:
            suggested = self.capacity
            rec = "OPTIMAL"
            reason = f"Cache size is balanced. Current hit rate is {stats.hit_ratio:.1f}% with strong cost-efficiency ROI ({roi}x)."

        return ScalingEvaluation(
            recommendation=rec,
            reason=reason,
            roi_ratio=roi,
            monthly_savings_proj_usd=monthly_savings_proj,
            monthly_capacity_cost_usd=current_monthly_ram_cost,
            suggested_capacity=suggested,
            current_capacity=self.capacity,
            current_hit_rate_pct=stats.hit_ratio,
        )
