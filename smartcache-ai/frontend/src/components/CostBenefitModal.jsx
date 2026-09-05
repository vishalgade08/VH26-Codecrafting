import React from 'react';
import { X, Scale, DollarSign, TrendingUp, Cpu, CheckCircle } from 'lucide-react';

export default function CostBenefitModal({ isOpen, onClose, scalingData }) {
  if (!isOpen) return null;

  const data = scalingData || {
    recommendation: 'OPTIMAL',
    reason: 'Cache size is balanced. Cost savings exceed memory overhead.',
    roi_ratio: 14.8,
    monthly_savings_proj_usd: 245.0,
    monthly_capacity_cost_usd: 2.50,
    suggested_capacity: 50,
    current_capacity: 50,
    current_hit_rate_pct: 82.5,
  };

  const isScaleUp = data.recommendation === 'SCALE_UP';
  const isScaleDown = data.recommendation === 'SCALE_DOWN';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="relative w-full max-w-xl rounded-2xl bg-slate-900 border border-slate-800 p-6 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Scale className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                Application Scaling & ROI Cost-Benefit Model
              </h3>
              <p className="text-xs text-slate-400">
                Evaluating cache auto-scaling vs backend regeneration expenses
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Recommendation Badge */}
        <div className="rounded-xl bg-slate-950/80 border border-slate-800 p-4 flex items-center justify-between">
          <div>
            <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold block">
              Auto-Scaling Action
            </span>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-lg font-black tracking-tight ${
                isScaleUp ? 'text-amber-400' : isScaleDown ? 'text-cyan-400' : 'text-emerald-400'
              }`}>
                {data.recommendation}
              </span>
              <span className="text-xs text-slate-400">
                (Suggested: {data.suggested_capacity} items vs Current: {data.current_capacity})
              </span>
            </div>
          </div>
          <div className="text-right">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold block">
              Net ROI Multiple
            </span>
            <span className="text-2xl font-black text-cyan-400">
              {data.roi_ratio}x
            </span>
          </div>
        </div>

        {/* Financial Breakdown Cards */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="rounded-xl bg-slate-950/60 border border-slate-800 p-3.5 space-y-1">
            <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
              <DollarSign className="h-4 w-4" />
              <span>Projected Savings / Mo</span>
            </div>
            <p className="text-xl font-extrabold text-white">
              ${(data.monthly_savings_proj_usd || 0).toFixed(2)}
            </p>
            <p className="text-[11px] text-slate-400">
              Avoided database & ML inference recomputations
            </p>
          </div>

          <div className="rounded-xl bg-slate-950/60 border border-slate-800 p-3.5 space-y-1">
            <div className="flex items-center gap-1.5 text-slate-300 font-semibold">
              <Cpu className="h-4 w-4 text-indigo-400" />
              <span>Cache RAM Cost / Mo</span>
            </div>
            <p className="text-xl font-extrabold text-white">
              ${(data.monthly_capacity_cost_usd || 0).toFixed(2)}
            </p>
            <p className="text-[11px] text-slate-400">
              Estimated infrastructure allocation for cache tier
            </p>
          </div>
        </div>

        {/* Reason / Narrative */}
        <div className="rounded-xl bg-indigo-950/30 border border-indigo-500/20 p-4 text-xs text-slate-300 leading-relaxed">
          <p className="font-semibold text-indigo-300 mb-1">Algorithmic Justification:</p>
          {data.reason}
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-2">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl transition-colors cursor-pointer"
          >
            Acknowledge & Close
          </button>
        </div>
      </div>
    </div>
  );
}
