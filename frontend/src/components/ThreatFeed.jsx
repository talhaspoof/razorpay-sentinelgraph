import React from 'react';
import { ShieldAlert, AlertTriangle, ShieldCheck, Zap, Users, Smartphone, CreditCard, ChevronRight } from 'lucide-react';

export default function ThreatFeed({ syndicates, onSelectSyndicate, onQuarantineCluster, selectedClusterId }) {
  if (!syndicates || syndicates.length === 0) {
    return (
      <div className="bg-[#111827] rounded-2xl border border-slate-800 p-6 flex flex-col items-center justify-center text-center h-[540px]">
        <ShieldCheck className="w-12 h-12 text-emerald-400 mb-3 animate-pulse" />
        <h3 className="text-base font-semibold text-slate-200">No Active Threats Detected</h3>
        <p className="text-xs text-slate-400 max-w-xs mt-1">
          The transaction graph is operating within nominal safety thresholds. Ingest transactions to trigger threat detection.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-[#111827] rounded-2xl border border-slate-800 p-5 flex flex-col h-[540px] shadow-2xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-red-400" />
          <h2 className="text-sm font-bold text-slate-200 tracking-wide uppercase">Detected Syndicates</h2>
        </div>
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
          {syndicates.length} Active
        </span>
      </div>

      <div className="overflow-y-auto space-y-3 mt-3 pr-1">
        {syndicates.map((syn) => {
          const isSelected = selectedClusterId === syn.cluster_id;
          const isQuarantined = syn.is_quarantined;

          return (
            <div
              key={syn.cluster_id}
              onClick={() => onSelectSyndicate(syn)}
              className={`p-4 rounded-xl border transition cursor-pointer relative overflow-hidden ${
                isSelected
                  ? 'bg-slate-800/80 border-blue-500 shadow-lg shadow-blue-500/10'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-850'
              }`}
            >
              {/* Severity Banner */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded uppercase tracking-wider ${
                    syn.severity === 'CRITICAL'
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                      : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  }`}>
                    {syn.severity}
                  </span>
                  <span className="mono-text text-xs text-slate-300 font-semibold">{syn.cluster_id.slice(0, 16)}</span>
                </div>
                <span className="mono-text text-xs font-bold text-red-400">
                  Risk: {Math.round(syn.risk_score * 100)}%
                </span>
              </div>

              {/* Entity Counts */}
              <div className="grid grid-cols-3 gap-2 py-2 border-y border-slate-800/60 text-xs text-slate-300">
                <div className="flex items-center gap-1.5">
                  <Users className="w-3.5 h-3.5 text-blue-400" />
                  <span>{syn.user_count} Users</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Smartphone className="w-3.5 h-3.5 text-purple-400" />
                  <span>{syn.device_count} Devices</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <CreditCard className="w-3.5 h-3.5 text-emerald-400" />
                  <span>{syn.card_count} Cards</span>
                </div>
              </div>

              {/* Signals */}
              <div className="mt-2 text-[11px] text-slate-400 space-y-1">
                {syn.signals?.map((sig, idx) => (
                  <div key={idx} className="flex items-start gap-1.5">
                    <span className="text-red-400">•</span>
                    <span className="truncate">{sig}</span>
                  </div>
                ))}
              </div>

              {/* Action Button */}
              <div className="mt-3 pt-2 flex items-center justify-between">
                {isQuarantined ? (
                  <span className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5" /> Quarantined
                  </span>
                ) : (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onQuarantineCluster(syn.cluster_id, syn.node_ids);
                    }}
                    className="text-[11px] font-bold px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white transition flex items-center gap-1 shadow-md shadow-red-600/20"
                  >
                    <Zap className="w-3 h-3" /> Isolate Syndicate
                  </button>
                )}
                <span className="text-xs text-slate-500 flex items-center gap-0.5">
                  Inspect <ChevronRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
