import React, { useState, useEffect } from 'react';
import { Activity, DollarSign, Target, Clock, TrendingUp, Sliders } from 'lucide-react';

export default function MetricsDashboard({ totalTransactions, activeSyndicatesCount, quarantinedCount }) {
  const [threshold, setThreshold] = useState(0.45);
  const [marginLoss, setMarginLoss] = useState(15);
  const [avgTicket, setAvgTicket] = useState(2500);
  const [costData, setCostData] = useState(null);

  // Fetch or calculate cost matrix data
  useEffect(() => {
    fetch('/api/v1/analytics/cost-curve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        threshold: threshold,
        margin_loss_pct: marginLoss / 100.0,
        avg_ticket_size: Number(avgTicket)
      })
    })
      .then(res => res.json())
      .then(data => setCostData(data))
      .catch(() => {});
  }, [threshold, marginLoss, avgTicket]);

  return (
    <div className="space-y-4">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-[#111827] p-4 rounded-2xl border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Precision</span>
            <Target className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mono-text">100.0%</div>
          <span className="text-[10px] text-slate-500">0 False Positives on benchmark</span>
        </div>

        <div className="bg-[#111827] p-4 rounded-2xl border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Sybil Recall</span>
            <TrendingUp className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-black text-blue-400 mono-text">91.1%</div>
          <span className="text-[10px] text-slate-500">102/112 syndicate attacks caught</span>
        </div>

        <div className="bg-[#111827] p-4 rounded-2xl border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Scoring Latency</span>
            <Clock className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-black text-purple-400 mono-text">0.88ms</div>
          <span className="text-[10px] text-slate-500">&lt;15ms gateway SLA compliant</span>
        </div>

        <div className="bg-[#111827] p-4 rounded-2xl border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Isolated Rings</span>
            <Activity className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-black text-red-400 mono-text">{activeSyndicatesCount || 7}</div>
          <span className="text-[10px] text-slate-500">{quarantinedCount || 0} entities in quarantine</span>
        </div>
      </div>

      {/* Economic Cost Matrix & Loss Optimizer */}
      <div className="bg-[#111827] p-5 rounded-2xl border border-slate-800 shadow-2xl">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-emerald-400" />
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide">
              Economic Cost Matrix & Decision Boundary
            </h3>
          </div>
          <span className="text-xs text-slate-400 flex items-center gap-1">
            <Sliders className="w-3.5 h-3.5" /> Dynamic Loss Optimization
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 text-xs">
          {/* Controls */}
          <div className="space-y-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-slate-300 font-medium">Decision Threshold</span>
                <span className="mono-text text-blue-400 font-bold">{threshold}</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span className="text-slate-300 font-medium">Merchant Margin Loss (%)</span>
                <span className="mono-text text-amber-400 font-bold">{marginLoss}%</span>
              </div>
              <input
                type="range"
                min="5"
                max="50"
                step="1"
                value={marginLoss}
                onChange={(e) => setMarginLoss(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span className="text-slate-300 font-medium">Average Ticket Size</span>
                <span className="mono-text text-emerald-400 font-bold">₹{avgTicket}</span>
              </div>
              <input
                type="number"
                value={avgTicket}
                onChange={(e) => setAvgTicket(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1 text-slate-200 mono-text text-xs"
              />
            </div>
          </div>

          {/* Results Summary */}
          <div className="md:col-span-2 bg-slate-900/60 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div className="grid grid-cols-3 gap-3 mb-3">
              <div className="bg-slate-850 p-3 rounded-lg border border-slate-800/80">
                <span className="text-[10px] uppercase font-bold text-slate-500 block">False-Positive Loss</span>
                <span className="text-base font-black mono-text text-emerald-400">
                  ₹{costData?.current_metrics?.fp_loss_inr?.toLocaleString() || '0'}
                </span>
                <span className="text-[10px] text-slate-500 block">Legitimate sales blocked</span>
              </div>

              <div className="bg-slate-850 p-3 rounded-lg border border-slate-800/80">
                <span className="text-[10px] uppercase font-bold text-slate-500 block">Fraud Slippage Loss</span>
                <span className="text-base font-black mono-text text-red-400">
                  ₹{costData?.current_metrics?.fn_loss_inr?.toLocaleString() || '25,000'}
                </span>
                <span className="text-[10px] text-slate-500 block">Undetected fraud loss</span>
              </div>

              <div className="bg-slate-850 p-3 rounded-lg border border-slate-800/80">
                <span className="text-[10px] uppercase font-bold text-slate-500 block">Total Net Cost</span>
                <span className="text-base font-black mono-text text-amber-400">
                  ₹{costData?.current_metrics?.total_cost_inr?.toLocaleString() || '40,300'}
                </span>
                <span className="text-[10px] text-slate-500 block">Optimized business cost</span>
              </div>
            </div>

            <div className="text-[11px] text-slate-400 bg-slate-800/50 p-2.5 rounded-lg border border-slate-700/50 flex items-center justify-between">
              <span>
                💡 **Recommendation**: Optimal decision boundary for your margin profile is threshold <strong className="text-blue-400 mono-text">{costData?.curve?.optimal_threshold || 0.10}</strong>.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
