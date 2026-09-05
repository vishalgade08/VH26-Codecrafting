import React from 'react';
import { Play, Pause, FastForward, Sliders, Layers } from 'lucide-react';

export default function SimulationControl({
  config,
  onChangeConfig,
  onStart,
  onStep,
  onStop,
  isRunning,
  progressPct,
  currentIndex,
  totalSteps,
  adaptiveWeights,
}) {
  const weights = adaptiveWeights || {
    frequency: 0.25,
    recency: 0.20,
    retrieval_cost: 0.25,
    latency: 0.10,
    popularity: 0.10,
    size_efficiency: 0.10,
  };

  return (
    <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sliders className="h-5 w-5 text-cyan-400" />
          <h2 className="text-lg font-bold text-white tracking-tight">
            Workload & Traffic Simulation Controls
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Progress:</span>
          <span className="text-xs font-mono font-bold text-cyan-400">
            {currentIndex || 0} / {totalSteps || config.request_count} ({progressPct || 0}%)
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
        <div
          className="h-full bg-gradient-to-r from-cyan-500 via-indigo-500 to-emerald-400 transition-all duration-300"
          style={{ width: `${Math.min(100, progressPct || 0)}%` }}
        />
      </div>

      {/* Control Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Workload Profile */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Workload Profile
          </label>
          <select
            value={config.workload_type}
            onChange={(e) => onChangeConfig({ ...config, workload_type: e.target.value })}
            disabled={isRunning}
            className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-2.5 text-xs text-white focus:border-cyan-500 focus:outline-none"
          >
            <option value="READ_HEAVY_API">⚡ Read-Heavy API (User / Meta)</option>
            <option value="COMPUTE_HEAVY_RECOMMENDATION">🧠 Compute-Heavy ML Rec</option>
          </select>
        </div>

        {/* Traffic Scenario */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Traffic Scenario
          </label>
          <select
            value={config.scenario}
            onChange={(e) => onChangeConfig({ ...config, scenario: e.target.value })}
            disabled={isRunning}
            className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-2.5 text-xs text-white focus:border-cyan-500 focus:outline-none"
          >
            <option value="STEADY_LOAD">📈 Steady Zipfian Load</option>
            <option value="SUDDEN_SPIKE">⚡ Sudden Viral Spike</option>
            <option value="POPULARITY_SHIFT">🔄 Dynamic Popularity Shift</option>
          </select>
        </div>

        {/* Cache Capacity Slider */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="font-semibold uppercase tracking-wider text-slate-400">Capacity</span>
            <span className="font-mono font-bold text-cyan-300">{config.cache_capacity} items</span>
          </div>
          <input
            type="range"
            min="10"
            max="150"
            step="5"
            value={config.cache_capacity}
            onChange={(e) => onChangeConfig({ ...config, cache_capacity: parseInt(e.target.value) })}
            disabled={isRunning}
            className="w-full accent-cyan-500"
          />
        </div>

        {/* Request Count Slider */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="font-semibold uppercase tracking-wider text-slate-400">Trace Size</span>
            <span className="font-mono font-bold text-indigo-300">{config.request_count} reqs</span>
          </div>
          <input
            type="range"
            min="100"
            max="800"
            step="50"
            value={config.request_count}
            onChange={(e) => onChangeConfig({ ...config, request_count: parseInt(e.target.value) })}
            disabled={isRunning}
            className="w-full accent-indigo-500"
          />
        </div>
      </div>

      {/* Action Buttons & Dynamic Weights Display */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-slate-800/80">
        {/* Playback Buttons */}
        <div className="flex items-center gap-2">
          {!isRunning ? (
            <button
              onClick={onStart}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-emerald-600/20 cursor-pointer"
            >
              <Play className="h-4 w-4 fill-white" />
              <span>{currentIndex > 0 ? 'Resume Simulation' : 'Start Simulation'}</span>
            </button>
          ) : (
            <button
              onClick={onStop}
              className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-bold transition-all shadow-md cursor-pointer"
            >
              <Pause className="h-4 w-4" />
              <span>Pause</span>
            </button>
          )}

          <button
            onClick={() => onStep(25)}
            className="flex items-center gap-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition-all border border-slate-700 cursor-pointer"
          >
            <FastForward className="h-3.5 w-3.5" />
            <span>Step +25</span>
          </button>
        </div>

        {/* Adaptive Weights Pills */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
          <span className="text-slate-400 font-semibold mr-1 flex items-center gap-1">
            <Layers className="h-3.5 w-3.5 text-cyan-400" />
            Weights:
          </span>
          {Object.entries(weights).map(([k, v]) => (
            <span
              key={k}
              className="px-2 py-0.5 rounded-md bg-slate-950 border border-slate-800 font-mono text-slate-300"
              title={`Adaptive weight for ${k}`}
            >
              <span className="text-slate-500">{k.slice(0, 4)}:</span>{' '}
              <span className="text-cyan-300 font-bold">{(v * 100).toFixed(0)}%</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
