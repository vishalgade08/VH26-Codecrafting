# SmartCache AI — Adaptive Application-Aware Cache Management System
**VCET Hackathon 2026** | **Domain:** Application Scaling

SmartCache AI is an intelligent, context-aware caching system that replaces naive recency/frequency heuristics (LRU/LFU) with a **dynamic multi-factor scoring engine**. It continuously balances data retrieval cost, latency SLAs, memory footprint, access frequency, recency, and popularity trends to maximize infrastructure cost savings and resilience under dynamic workloads.

---

## Key Features

1. **Adaptive Multi-Factor Scoring Engine**:
   - Scores every cached entry on a dynamic composite scale (0 to 100):
     $$\text{Score} = w_f \cdot F + w_r \cdot R + w_c \cdot C + w_l \cdot L + w_p \cdot P + w_s \cdot S$$
   - **$F$ (Frequency)**: Normalized cumulative hit volume.
   - **$R$ (Recency)**: Exponential half-life decay function ($t_{1/2} = 8\text{s}$).
   - **$C$ (Retrieval Cost)**: Dollar expenditure required to re-fetch/recompute from database or upstream API.
   - **$L$ (Latency Penalty)**: Downstream round-trip time saved by avoiding backend regeneration.
   - **$P$ (Popularity Trend)**: Velocity of requests over time, identifying viral spikes before LRU adapts.
   - **$S$ (Size Efficiency)**: Logarithmic byte efficiency favoring compact entries under memory constraints.
   - **Adaptive Pressure Reweighting**: System dynamically increases $w_c$ under high backend load, $w_s$ under memory pressure (>80%), and $w_p$ during traffic surges.

2. **4 Action States**:
   - `RETAIN` ($\text{Score} \ge 75$): Guaranteed residency in high-speed RAM tier.
   - `MONITOR` ($50 \le \text{Score} < 75$): Monitored for trending shifts.
   - `EVICT` ($\text{Score} < 50$): Candidate for deterministic eviction when capacity threshold is hit.
   - `REFRESH` ($\text{is\_stale} \land \text{Score} \ge 60$): Proactively re-fetched in background before client miss occurs.

3. **Dynamic Workload & Traffic Simulator**:
   - **Workloads**:
     - *Read-Heavy API*: Fast, lightweight entity queries (15–65ms, $0.0005–$0.0025 cost, 0.5–4 KB).
     - *Compute-Heavy Recommendation*: Expensive ML embeddings & vector queries (250–1100ms, $0.020–$0.085 cost, 10–80 KB).
   - **Traffic Scenarios**:
     - *Steady Zipfian Load*: Power-law distribution simulating realistic production access.
     - *Sudden Viral Spike*: High-intensity burst on emergent keys.
     - *Popularity Shift*: Dynamic drift in active interest, testing cold-start resilience and cache churn.

4. **4-Way Comparative Benchmarking Engine**:
   - Concurrently executes identical request traces across:
     1. **SmartCache AI**
     2. **Standard LRU**
     3. **Standard LFU**
     4. **GreedyDual-Size Frequency (GDSF)**
   - Metrics tracked: Hit Ratio (%), Cost-Weighted Hit Ratio (%), Total Dollar Savings ($), Blended Latency (ms), and Eviction Counts.

5. **Application Scaling & Cost-Benefit (ROI) Engine**:
   - Quantifies memory RAM expenditure vs backend savings.
   - Evaluates auto-scaling recommendations (`SCALE_UP`, `OPTIMAL`, `SCALE_DOWN`) with projected monthly ROI multiples.

6. **Real-Time Interactive Dashboard**:
   - Built with React, Vite, and Tailwind CSS.
   - Live telemetry cards, interactive simulation controls, side-by-side benchmark bars, and a scrolling live decision feed.

---

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, Pytest
- **Frontend**: React 18, Vite 6, Tailwind CSS 3, Lucide React
- **Storage & Infrastructure**: Redis, PostgreSQL, Docker Compose

---

## Directory Structure

```text
smartcache-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes_cache.py       # Cache CRUD, scaling evaluation, decisions
│   │   │   ├── routes_benchmark.py   # 4-way comparative benchmark runner
│   │   │   └── routes_simulator.py   # Dynamic simulation state machine & telemetry
│   │   ├── cache/
│   │   │   ├── base.py               # Abstract BaseCache interface
│   │   │   ├── scoring.py            # DynamicScorer with 6 adaptive factors
│   │   │   ├── smart_cache.py        # SmartCache AI core engine
│   │   │   ├── lru.py                # Baseline LRU
│   │   │   ├── lfu.py                # Baseline LFU
│   │   │   └── gds.py                # Baseline GDSF
│   │   ├── core/
│   │   │   ├── config.py             # Global settings & cost constants
│   │   │   └── models.py             # Pydantic schemas
│   │   ├── simulator/
│   │   │   ├── workloads.py          # Read-heavy and ML recommendation models
│   │   │   ├── traffic_generator.py  # Zipfian, Spike, and Shift generators
│   │   │   └── benchmark_runner.py   # Multi-cache comparative benchmark harness
│   │   └── main.py                   # FastAPI application assembly & CORS
│   └── tests/
│       ├── test_health.py            # Health verification
│       ├── test_scoring.py           # Multi-factor score & threshold unit tests
│       ├── test_cache_policies.py    # Policy comparison tests (SmartCache vs LRU)
│       └── test_simulator.py         # Workload, traffic, and benchmark tests
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx            # Brand, status pills, scaling ROI trigger
│   │   │   ├── MetricsCards.jsx      # Live cost-weighted hit rate, savings, latency
│   │   │   ├── SimulationControl.jsx # Sliders, workload/scenario pickers, playback
│   │   │   ├── BenchmarkChart.jsx    # Side-by-side 4-algorithm benchmark bars
│   │   │   ├── LiveDecisionStream.jsx# Real-time scrolling score breakdown feed
│   │   │   └── CostBenefitModal.jsx  # Scaling analysis & financial ROI model
│   │   ├── services/
│   │   │   └── api.js                # Complete async API client
│   │   ├── App.jsx                   # Dashboard orchestration
│   │   └── index.css                 # Styling
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Running the Application

### 1. Automated Backend Tests
Run the test suite verifying all 10 unit and policy test cases:
```bash
cd smartcache-ai
$env:PYTHONPATH = "backend"
pytest backend/tests -v
```

### 2. Start Backend Server
```bash
cd smartcache-ai
$env:PYTHONPATH = "backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 3. Start Frontend Dashboard
```bash
cd smartcache-ai/frontend
npm run dev
```
- Dashboard UI: [http://localhost:5173](http://localhost:5173)

### 4. Running with Docker Compose
```bash
docker-compose up --build
```
