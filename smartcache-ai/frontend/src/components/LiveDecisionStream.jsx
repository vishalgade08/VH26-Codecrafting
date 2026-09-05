import React from 'react';
import { Eye, Shield, AlertTriangle, RefreshCw, Trash2 } from 'lucide-react';

export default function LiveDecisionStream({ decisions }) {
  const list = decisions || [];

  const getActionBadge = (action) => {
    switch (action) {
      case 'RETAIN':
        return (
          <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            <Shield className="h-3 w-3" />
            RETAIN
          </span>
        );
      case 'EVICT':
        return (
          <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-rose-500/20 text-rose-300 border border-rose-500/30">
            <Trash2 className="h-3 w-3" />
            EVICT
          </span>
        );
      case 'REFRESH':
        return (
          <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-purple-500/20 text-purple-300 border border-purple-500/30">
            <RefreshCw className="h-3 w-3" />
            REFRESH
          </span>
        );
      case 'MONITOR':
      default:
        return (
          <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
            <Eye className="h-3 w-3" />
            MONITOR
          </span>
        );
    }
  };

  return (
    <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 shadow-xl space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Eye className="h-5 w-5 text-cyan-400" />
          <h2 className="text-lg font-bold text-white tracking-tight">
            Live Adaptive Decision Stream
          </h2>
        </div>
        <span className="text-xs text-slate-400">
          Showing last {list.length} multi-factor evaluations
        </span>
      </div>

      {/* Stream List */}
      <div className="space-y-2.5 max-h-96 overflow-y-auto pr-1">
        {list.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">
            No decision events recorded yet. Start simulation or send requests to see decisions.
          </div>
        ) : (
          list.map((event, idx) => (
            <div
              key={`${event.key}-${event.timestamp}-${idx}`}
              className="rounded-xl bg-slate-950/60 border border-slate-800/80 p-3.5 space-y-2 hover:border-slate-700 transition-colors"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  {getActionBadge(event.action)}
                  <span className="font-mono text-xs font-bold text-white">
                    {event.key}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">Score:</span>
                  <span className={`text-xs font-mono font-bold ${
                    event.score >= 75 ? 'text-emerald-400' : event.score >= 50 ? 'text-cyan-400' : 'text-rose-400'
                  }`}>
                    {event.score.toFixed(1)} / 100
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300">
                {event.justification}
              </p>

              {/* Factors mini bar */}
              {event.factors && (
                <div className="grid grid-cols-6 gap-1 pt-1.5 border-t border-slate-800/50 text-[10px]">
                  {Object.entries(event.factors).map(([factor, val]) => (
                    <div key={factor} className="bg-slate-900/80 rounded px-1.5 py-1 text-center">
                      <span className="text-slate-500 block uppercase tracking-wider text-[8px]">
                        {factor.slice(0, 4)}
                      </span>
                      <span className="font-mono font-bold text-slate-300">
                        {val !== undefined ? val.toFixed(0) : 0}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
