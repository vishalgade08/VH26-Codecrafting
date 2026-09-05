import math
import time
from typing import Dict, Tuple
from app.core.models import CacheItem, ScoreBreakdown, DecisionAction


class DynamicScorer:
    """
    Multi-Factor Adaptive Scoring Engine for SmartCache AI.
    Combines Frequency, Recency, Retrieval Cost, Latency, Popularity Trend, and Size Efficiency.
    Dynamically adjusts weightings in response to runtime system pressure.
    """

    def __init__(self):
        self.base_weights = {
            "frequency": 0.25,
            "recency": 0.20,
            "retrieval_cost": 0.25,
            "latency": 0.10,
            "popularity": 0.10,
            "size_efficiency": 0.10,
        }

    @property
    def weights(self) -> Dict[str, float]:
        return self.base_weights

    def compute_factors(self, item: CacheItem, now: float, max_freq: int = 50) -> Dict[str, float]:
        norm_freq = min(100.0, (item.access_count / max(max_freq, 1)) * 100.0)

        delta_t = max(0.0, now - item.last_accessed_at)
        half_life = 8.0  # seconds
        norm_recency = max(0.0, min(100.0, 100.0 * math.exp(-delta_t / half_life)))

        norm_cost = min(100.0, (item.retrieval_cost_usd / 0.05) * 100.0)
        norm_latency = min(100.0, (item.retrieval_latency_ms / 1000.0) * 100.0)

        age = max(1.0, now - item.created_at)
        velocity = item.access_count / age
        norm_popularity = min(100.0, velocity * 25.0)

        size_kb = max(item.size_bytes / 1024.0, 0.1)
        norm_size_eff = max(0.0, min(100.0, 100.0 / (1.0 + math.log10(max(1.0, size_kb * 10.0)))))

        return {
            "frequency": round(norm_freq, 2),
            "recency": round(norm_recency, 2),
            "retrieval_cost": round(norm_cost, 2),
            "latency": round(norm_latency, 2),
            "popularity": round(norm_popularity, 2),
            "size_efficiency": round(norm_size_eff, 2),
        }

    def get_adaptive_weights(
        self,
        memory_pressure_ratio: float = 0.5,
        db_pressure_ratio: float = 0.5,
        traffic_burst_ratio: float = 0.5,
    ) -> Dict[str, float]:
        w = dict(self.base_weights)

        if memory_pressure_ratio > 0.8:
            w["size_efficiency"] += 0.15
            w["frequency"] -= 0.05
            w["recency"] -= 0.10

        if db_pressure_ratio > 0.7:
            w["retrieval_cost"] += 0.10
            w["latency"] += 0.05
            w["frequency"] -= 0.10
            w["popularity"] -= 0.05

        if traffic_burst_ratio > 0.7:
            w["popularity"] += 0.10
            w["recency"] += 0.05
            w["size_efficiency"] = max(0.05, w["size_efficiency"] - 0.10)

        total = sum(w.values())
        return {k: round(v / total, 3) for k, v in w.items()}

    def score_item(
        self,
        item: CacheItem,
        now: float,
        memory_pressure: float = 0.5,
        db_pressure: float = 0.5,
        traffic_burst: float = 0.5,
        max_freq: int = 50,
    ) -> ScoreBreakdown:
        factors = self.compute_factors(item, now, max_freq=max_freq)
        weights = self.get_adaptive_weights(
            memory_pressure_ratio=memory_pressure,
            db_pressure_ratio=db_pressure,
            traffic_burst_ratio=traffic_burst,
        )

        score = sum(factors[factor] * weights[factor] for factor in factors)
        final_score = round(score, 2)

        is_stale = item.is_stale or ((now - item.created_at) > item.ttl_seconds)

        decision, justification = self.decide_action(final_score, is_stale, factors)

        breakdown = ScoreBreakdown(
            frequency=factors["frequency"],
            recency=factors["recency"],
            retrieval_cost=factors["retrieval_cost"],
            latency=factors["latency"],
            popularity=factors["popularity"],
            size_efficiency=factors["size_efficiency"],
            final_score=final_score,
            decision=decision,
            weights=weights,
            justification=justification,
        )

        item.current_score = final_score
        item.score_breakdown = breakdown
        return breakdown

    def decide_action(
        self, score: float, is_stale: bool, factors: Dict[str, float]
    ) -> Tuple[DecisionAction, str]:
        if is_stale and score >= 60.0:
            return (
                DecisionAction.REFRESH,
                f"High-value object (score {score}) is stale; proactively refreshing from source",
            )

        if score >= 80.0:
            top_factor = max(factors.keys(), key=lambda k: factors[k])
            return (
                DecisionAction.RETAIN,
                f"High retention priority (score {score}) driven by strong {top_factor}",
            )
        elif score >= 50.0:
            return (
                DecisionAction.MONITOR,
                f"Moderate priority (score {score}); monitored for trending shifts",
            )
        else:
            return (
                DecisionAction.EVICT,
                f"Low utility score ({score}); prime candidate for replacement",
            )


scorer = DynamicScorer()
