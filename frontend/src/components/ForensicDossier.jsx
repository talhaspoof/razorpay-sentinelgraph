import React from 'react';
import { FileText, ShieldAlert, CheckCircle2, Download, AlertOctagon, Key, ExternalLink } from 'lucide-react';

export default function ForensicDossier({ investigation, onExportDossier }) {
  if (!investigation) {
    return (
      <div className="bg-[#111827] rounded-2xl border border-slate-800 p-6 flex flex-col items-center justify-center text-center h-[340px]">
        <FileText className="w-10 h-10 text-slate-600 mb-2" />
        <h4 className="text-sm font-semibold text-slate-300">No Active Forensic Investigation</h4>
        <p className="text-xs text-slate-500 max-w-xs mt-1">
          Select an entity or trigger a simulated attack to generate an autonomous AI forensic threat dossier.
        </p>
      </div>
    );
  }

  const { attack_vector, threat_summary, iocs, mitre_tactics, recommended_action, dispute_dossier, tx_id, user_id } = investigation;

  return (
    <div className="bg-[#111827] rounded-2xl border border-slate-800 p-5 flex flex-col shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <AlertOctagon className="w-5 h-5 text-amber-400" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide">AI Forensic Threat Dossier</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="mono-text text-xs px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20 font-semibold">
            {attack_vector || 'ANOMALOUS_CLUSTER'}
          </span>
          <button
            onClick={() => onExportDossier && onExportDossier(investigation)}
            className="flex items-center gap-1 text-xs font-semibold px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-md transition border border-slate-700"
          >
            <Download className="w-3.5 h-3.5" /> Export Pack
          </button>
        </div>
      </div>

      <div className="space-y-4 mt-4 text-xs">
        {/* Narrative Summary */}
        <div className="bg-slate-900/80 p-3.5 rounded-xl border border-slate-800">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            Autonomous Attack Narrative
          </span>
          <p className="text-slate-200 leading-relaxed text-xs">
            {threat_summary}
          </p>
        </div>

        {/* Indicators of Compromise & MITRE Mapping */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {/* IOCs */}
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <span className="text-[11px] font-bold text-red-400 uppercase tracking-wider block mb-2 flex items-center gap-1">
              <Key className="w-3.5 h-3.5" /> Verified IOCs
            </span>
            <ul className="space-y-1.5 text-slate-300">
              {iocs && iocs.length > 0 ? (
                iocs.map((ioc, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-red-400">▹</span>
                    <span className="mono-text text-[11px]">{ioc}</span>
                  </li>
                ))
              ) : (
                <li className="text-slate-500">No high-severity IOCs flagged.</li>
              )}
            </ul>
          </div>

          {/* MITRE ATT&CK */}
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <span className="text-[11px] font-bold text-purple-400 uppercase tracking-wider block mb-2">
              MITRE ATT&CK Mapping
            </span>
            <div className="flex flex-wrap gap-1.5">
              {mitre_tactics && mitre_tactics.length > 0 ? (
                mitre_tactics.map((t, idx) => (
                  <span key={idx} className="text-[10px] mono-text px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">
                    {t}
                  </span>
                ))
              ) : (
                <span className="text-slate-500 text-[11px]">No external tactics mapped.</span>
              )}
            </div>

            <div className="mt-3 pt-2 border-t border-slate-800/80">
              <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider block mb-1">
                Recommended Policy
              </span>
              <span className="mono-text text-xs text-emerald-300 font-bold">
                {recommended_action || 'STEP_UP_AUTHENTICATION'}
              </span>
            </div>
          </div>
        </div>

        {/* Dispute Pack Preview */}
        {dispute_dossier && (
          <div className="bg-blue-950/30 border border-blue-900/50 p-3 rounded-xl">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[11px] font-bold text-blue-300 uppercase tracking-wider flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" /> Pre-Emptive Razorpay Dispute Defense Pack
              </span>
              <span className="mono-text text-[10px] text-blue-400">{dispute_dossier.dossier_id}</span>
            </div>
            <p className="text-slate-300 text-[11px] italic">
              "{dispute_dossier.recommended_bank_narrative}"
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
