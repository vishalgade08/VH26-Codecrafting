import React from 'react';
import { TrendingUp, Zap, Activity, Database } from 'lucide-react';

export default function MetricsCards({ stats, memoryPressurePct }) {
  const s = stats || {};
  const hitRatio = s.hit_ratio !== undefined ? s.hit_ratio : 0;
  const costWeightedRatio = s.cost_weighted_hit_ratio !== undefined ? s.cost_weighted_hit_ratio : 0;
  const costSaved = s.total_cost_saved_usd !== undefined ? s.total_cost_saved_usd : 0;
  const costIncurred = s.backend_cost_incurred_usd !== undefined ? s.backend_cost_incurred_usd : 0;
  const avgLatency = s.avg_latency_ms !== undefined ? s.avg_latency_ms : 0.5;
  const currentSize = s.current_size_items || 0;
  const maxCap = s.max_capacity_items || 50;
  const evictions = s.evictions || 0;
  const refreshes = s.refreshes || 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Cost-Weighted Hit Rate */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/90 border border-slate-800 p-5 shadow-lg">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Cost-Weighted Hit Rate
          </span>
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <TrendingUp className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-extrabold tracking-tight text-white">
            {costWeightedRatio.toFixed(1)}%
          </span>
          <span className="text-xs text-cyan-400 font-semibold">
            ({hitRatio.toFixed(1)}% raw)
          </span>
        </div>
        <p className="mt-2 text-xs text-slate-400">
          Prioritizes expensive compute over trivial responses.
        </p>
      </div>

      {/* 2. Total Cost Saved */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/90 border border-slate-800 p-5 shadow-lg">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Cost Saved (Backend Avoided)
          </span>
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Zap className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-extrabold tracking-tight text-emerald-400">
            ${costSaved.toFixed(3)}
          </span>
        </div>
        <p className="mt-2 text-xs text-slate-400">
          Incurred miss cost: <span className="text-rose-400">${costIncurred.toFixed(3)}</span>
        </p>
      </div>

      {/* 3. Average Response Latency */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/90 border border-slate-800 p-5 shadow-lg">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Avg Request Latency
          </span>
          <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Activity className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-extrabold tracking-tight text-indigo-300">
            {avgLatency.toFixed(1)} ms
          </span>
          <span className="text-xs text-slate-500 font-medium">blended</span>
        </div>
        <p className="mt-2 text-xs text-slate-400">
          Cache hits serve in ~0.5ms vs 50–1100ms backend latency.
        </p>
      </div>

      {/* 4. Cache Capacity & Pressure */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/90 border border-slate-800 p-5 shadow-lg">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Memory Pressure & Usage
          </span>
          <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Database className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          <span className="text-2xl font-extrabold tracking-tight text-white">
            {currentSize} / {maxCap}
          </span>
          <span className="text-xs font-bold text-amber-400">
            {(memoryPressurePct || (currentSize / maxCap * 100)).toFixed(0)}%
          </span>
        </div>
        <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-amber-500 rounded-full transition-all duration-300"
            style={{ width: `${Math.min(100, memoryPressurePct || (currentSize / maxCap * 100))}%` }}
          />
        </div>
        <p className="mt-2 text-xs text-slate-400">
          {evictions} evictions • {refreshes} proactive refreshes
        </p>
      </div>
    </div>
  );
}
