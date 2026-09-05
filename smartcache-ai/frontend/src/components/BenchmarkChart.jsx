import React from 'react';
import { BarChart3, Award, ArrowUpRight, CheckCircle2 } from 'lucide-react';

export default function BenchmarkChart({ benchmark, onRunBenchmark, isBenchmarking }) {
  if (!benchmark || !benchmark.algorithms) {
    return (
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-8 text-center">
        <p className="text-slate-400 text-sm">No benchmark data loaded yet.</p>
        <button
          onClick={onRunBenchmark}
          className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-xs font-semibold text-white cursor-pointer"
        >
          Run Initial Benchmark
        </button>
      </div>
    );
  }

  const { algorithms, winner, cost_savings_diff_vs_lru_pct, summary, workload, scenario } = benchmark;
  const algos = Object.entries(algorithms);

  // Find maximums for bar scaling
  const maxHitRate = 100;
  const maxCostSaved = Math.max(...algos.map(([_, a]) => a.total_cost_saved_usd || 0), 0.001);

  return (
    <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-white tracking-tight">
              4-Way Comparative Algorithmic Benchmark
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Evaluating identical request sequences across caching strategies under {scenario} ({workload}).
          </p>
        </div>

        <button
          onClick={onRunBenchmark}
          disabled={isBenchmarking}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-md cursor-pointer ${
            isBenchmarking
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white shadow-indigo-600/20'
          }`}
        >
          {isBenchmarking ? (
            <>
              <span className="h-3 w-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Running Trace...
            </>
          ) : (
            <>
              <ArrowUpRight className="h-4 w-4" />
              Run 4-Way Comparison
            </>
          )}
        </button>
      </div>

      {/* Summary Highlight Alert */}
      <div className="rounded-xl bg-gradient-to-r from-cyan-950/40 via-indigo-950/40 to-slate-900 border border-cyan-500/30 p-4 flex items-center gap-4">
        <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 shrink-0">
          <Award className="h-6 w-6" />
        </div>
        <div className="text-xs space-y-1">
          <div className="font-bold text-cyan-200 flex items-center gap-2">
            <span>Winner: {winner}</span>
            {cost_savings_diff_vs_lru_pct > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">
                +{cost_savings_diff_vs_lru_pct}% vs LRU
              </span>
            )}
          </div>
          <p className="text-slate-300 leading-relaxed">{summary}</p>
        </div>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {algos.map(([name, stats]) => {
          const isSmart = name.includes('SmartCache');
          const isWinner = name === winner;

          return (
            <div
              key={name}
              className={`rounded-xl p-5 border transition-all relative ${
                isSmart
                  ? 'bg-slate-950/90 border-cyan-500/50 shadow-lg shadow-cyan-500/5 ring-1 ring-cyan-500/20'
                  : 'bg-slate-950/40 border-slate-800/80 hover:border-slate-700'
              }`}
            >
              {/* Badges */}
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className={`text-xs font-bold ${isSmart ? 'text-cyan-300' : 'text-slate-300'}`}>
                  {name}
                </span>
                {isSmart && (
                  <span className="px-2 py-0.5 text-[9px] font-extrabold uppercase tracking-wider rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                    Adaptive
                  </span>
                )}
                {!isSmart && isWinner && (
                  <span className="px-2 py-0.5 text-[9px] font-extrabold uppercase tracking-wider rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    Winner
                  </span>
                )}
              </div>

              {/* Core Metrics */}
              <div className="space-y-3 text-xs">
                {/* Cost-Weighted Hit Ratio */}
                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>Cost-Weighted Hit %</span>
                    <span className="font-bold text-white">
                      {(stats.cost_weighted_hit_ratio || stats.hit_ratio || 0).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        isSmart ? 'bg-gradient-to-r from-cyan-400 to-indigo-500' : 'bg-slate-600'
                      }`}
                      style={{ width: `${Math.min(100, stats.cost_weighted_hit_ratio || stats.hit_ratio || 0)}%` }}
                    />
                  </div>
                </div>

                {/* Raw Hit Ratio */}
                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>Standard Hit Rate</span>
                    <span className="font-medium text-slate-300">
                      {(stats.hit_ratio || 0).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="h-full bg-slate-600 rounded-full"
                      style={{ width: `${Math.min(100, stats.hit_ratio || 0)}%` }}
                    />
                  </div>
                </div>

                {/* Cost Saved */}
                <div className="pt-2 border-t border-slate-800/60 flex justify-between items-baseline">
                  <span className="text-slate-400">Cost Saved:</span>
                  <span className={`text-sm font-extrabold ${isSmart ? 'text-emerald-400' : 'text-slate-200'}`}>
                    ${(stats.total_cost_saved_usd || 0).toFixed(3)}
                  </span>
                </div>

                {/* Avg Latency */}
                <div className="flex justify-between items-baseline">
                  <span className="text-slate-400">Avg Latency:</span>
                  <span className="font-semibold text-slate-200">
                    {(stats.avg_latency_ms || 0).toFixed(1)} ms
                  </span>
                </div>

                {/* Evictions */}
                <div className="flex justify-between items-baseline">
                  <span className="text-slate-400">Evictions:</span>
                  <span className="text-slate-400">
                    {stats.evictions || 0}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
