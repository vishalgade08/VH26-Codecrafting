import React, { useState, useEffect, useRef } from 'react';
import Navbar from './components/Navbar';
import MetricsCards from './components/MetricsCards';
import SimulationControl from './components/SimulationControl';
import BenchmarkChart from './components/BenchmarkChart';
import LiveDecisionStream from './components/LiveDecisionStream';
import CostBenefitModal from './components/CostBenefitModal';
import {
  checkHealth,
  getCacheStats,
  getScalingAnalysis,
  getLatestBenchmark,
  runBenchmark,
  startSimulation,
  stepSimulation,
  getTelemetry,
  stopSimulation,
  resetCache,
} from './services/api';

export default function App() {
  const [backendHealthy, setBackendHealthy] = useState(false);
  const [isROIModalOpen, setIsROIModalOpen] = useState(false);
  const [isBenchmarking, setIsBenchmarking] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  const [simConfig, setSimConfig] = useState({
    workload_type: 'READ_HEAVY_API',
    scenario: 'STEADY_LOAD',
    cache_capacity: 50,
    request_count: 500,
    unique_keys: 120,
    spike_multiplier: 3.0,
  });

  const [telemetry, setTelemetry] = useState({
    stats: null,
    recentDecisions: [],
    adaptiveWeights: {},
    currentIndex: 0,
    totalSteps: 500,
    progressPct: 0,
    memoryPressurePct: 0,
  });

  const [benchmark, setBenchmark] = useState(null);
  const [scalingData, setScalingData] = useState(null);

  const runningRef = useRef(isRunning);
  runningRef.current = isRunning;

  // Poll Health
  const pollHealth = async () => {
    const res = await checkHealth();
    setBackendHealthy(res.success && res.data?.status === 'healthy');
  };

  // Fetch initial telemetry & latest benchmark
  const loadInitialData = async () => {
    const [benchRes, teleRes] = await Promise.all([
      getLatestBenchmark(),
      getTelemetry(),
    ]);

    if (benchRes.success) {
      setBenchmark(benchRes.data);
    }
    if (teleRes.success) {
      const d = teleRes.data;
      setTelemetry({
        stats: d.stats,
        recentDecisions: d.recent_decisions || [],
        adaptiveWeights: d.adaptive_weights || {},
        currentIndex: d.current_index || 0,
        totalSteps: d.total_steps || 500,
        progressPct: d.progress_pct || 0,
        memoryPressurePct: d.memory_pressure_pct || 0,
      });
      setIsRunning(d.is_running || false);
    }
  };

  useEffect(() => {
    pollHealth();
    loadInitialData();
    const healthInterval = setInterval(pollHealth, 5000);
    return () => clearInterval(healthInterval);
  }, []);

  // Live simulation stepping loop
  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(async () => {
      if (!runningRef.current) return;
      const res = await stepSimulation(15);
      if (res.success) {
        const d = res.data;
        setTelemetry({
          stats: d.stats,
          recentDecisions: d.recent_decisions || [],
          adaptiveWeights: d.adaptive_weights || {},
          currentIndex: d.current_index || 0,
          totalSteps: d.total_steps || 500,
          progressPct: d.progress_pct || 0,
          memoryPressurePct: d.memory_pressure_pct || 0,
        });
        if (!d.is_running) {
          setIsRunning(false);
        }
      } else {
        setIsRunning(false);
      }
    }, 450);

    return () => clearInterval(interval);
  }, [isRunning]);

  // Handlers
  const handleStartSimulation = async () => {
    const res = await startSimulation(simConfig);
    if (res.success) {
      setIsRunning(true);
    }
  };

  const handleStepSimulation = async (batch = 25) => {
    const res = await stepSimulation(batch);
    if (res.success) {
      const d = res.data;
      setTelemetry({
        stats: d.stats,
        recentDecisions: d.recent_decisions || [],
        adaptiveWeights: d.adaptive_weights || {},
        currentIndex: d.current_index || 0,
        totalSteps: d.total_steps || 500,
        progressPct: d.progress_pct || 0,
        memoryPressurePct: d.memory_pressure_pct || 0,
      });
      if (!d.is_running) setIsRunning(false);
    }
  };

  const handleStopSimulation = async () => {
    await stopSimulation();
    setIsRunning(false);
  };

  const handleRunBenchmark = async () => {
    setIsBenchmarking(true);
    const res = await runBenchmark(simConfig);
    if (res.success) {
      setBenchmark(res.data);
    }
    setIsBenchmarking(false);
  };

  const handleOpenROI = async () => {
    const res = await getScalingAnalysis();
    if (res.success) {
      setScalingData(res.data);
    }
    setIsROIModalOpen(true);
  };

  const handleReset = async () => {
    await resetCache();
    await loadInitialData();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-slate-950">
      <Navbar
        backendHealthy={backendHealthy}
        onOpenROI={handleOpenROI}
        onReset={handleReset}
        isRunning={isRunning}
        workload={simConfig.workload_type}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Metric Summary Cards */}
        <MetricsCards
          stats={telemetry.stats}
          memoryPressurePct={telemetry.memoryPressurePct}
        />

        {/* Simulation Controls */}
        <SimulationControl
          config={simConfig}
          onChangeConfig={setSimConfig}
          onStart={handleStartSimulation}
          onStep={handleStepSimulation}
          onStop={handleStopSimulation}
          isRunning={isRunning}
          progressPct={telemetry.progressPct}
          currentIndex={telemetry.currentIndex}
          totalSteps={telemetry.totalSteps}
          adaptiveWeights={telemetry.adaptiveWeights}
        />

        {/* 4-Way Algorithmic Benchmark */}
        <BenchmarkChart
          benchmark={benchmark}
          onRunBenchmark={handleRunBenchmark}
          isBenchmarking={isBenchmarking}
        />

        {/* Live Decision Feed */}
        <LiveDecisionStream
          decisions={telemetry.recentDecisions}
        />
      </main>

      {/* Auto-Scaling Cost-Benefit Modal */}
      <CostBenefitModal
        isOpen={isROIModalOpen}
        onClose={() => setIsROIModalOpen(false)}
        scalingData={scalingData}
      />

      <footer className="border-t border-slate-900 bg-slate-950/50 py-4 px-6 text-center text-xs text-slate-600">
        SmartCache AI — VCET Hackathon 2026 (Domain: Application Scaling) • Multi-Factor Adaptive Cache Management System
      </footer>
    </div>
  );
}
