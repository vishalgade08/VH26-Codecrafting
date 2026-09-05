import random
from typing import Dict, Any
from app.core.models import CacheItem, WorkloadType


class WorkloadTemplate:
    """Generates realistic workload items with application-specific cost and latency profiles."""

    @staticmethod
    def generate_item(key: str, workload_type: WorkloadType) -> CacheItem:
        if workload_type == WorkloadType.READ_HEAVY_API:
            # Read-heavy API (User profiles, catalog metadata)
            size_bytes = random.randint(512, 4096)  # 0.5KB - 4KB
            retrieval_cost_usd = round(random.uniform(0.0005, 0.0025), 5)
            retrieval_latency_ms = round(random.uniform(15.0, 65.0), 1)
            ttl_seconds = float(random.choice([120, 300, 600]))
            value = {
                "endpoint": f"/api/v1/entities/{key}",
                "status": 200,
                "payload_size": size_bytes
            }
        else:
            # Compute-heavy recommendation (ML models, vector searches, aggregated reports)
            size_bytes = random.randint(10240, 81920)  # 10KB - 80KB
            # High computational regeneration cost ($0.02 - $0.08)
            retrieval_cost_usd = round(random.uniform(0.020, 0.085), 4)
            # High backend computation latency (250ms - 1100ms)
            retrieval_latency_ms = round(random.uniform(250.0, 1100.0), 1)
            ttl_seconds = float(random.choice([300, 900, 1800]))
            value = {
                "pipeline": "embedding-v2-recommendation",
                "scores": [random.random() for _ in range(10)],
                "computed_cost": retrieval_cost_usd
            }

        return CacheItem(
            key=key,
            value=value,
            size_bytes=size_bytes,
            retrieval_cost_usd=retrieval_cost_usd,
            retrieval_latency_ms=retrieval_latency_ms,
            ttl_seconds=ttl_seconds
        )
