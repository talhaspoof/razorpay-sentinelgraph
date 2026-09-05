import React, { useState } from 'react';
import { Bot, Send, Sparkles, User } from 'lucide-react';

export default function ThreatCopilot() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hello! I am Sentinel Co-Pilot. I can answer questions about detected fraud syndicates, investigate specific hardware/card clusters, or summarize active threat levels across the Razorpay graph."
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (queryText) => {
    const textToSend = queryText || input;
    if (!textToSend.trim()) return;

    const userMsg = { role: 'user', text: textToSend };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/v1/copilot/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: textToSend })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', text: data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', text: "Unable to query graph co-pilot backend. Ensure FastAPI server is running." }]);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    "What are the top detected fraud syndicates?",
    "Explain the Carding attack pattern",
    "Are there any quarantined devices?",
    "Give me an overall risk health summary"
  ];

  return (
    <div className="bg-[#111827] rounded-2xl border border-slate-800 p-5 flex flex-col h-[400px] shadow-2xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-200">Sentinel Threat Co-Pilot</h3>
            <span className="text-[10px] text-slate-500">Autonomous Graph Threat Hunting Assistant</span>
          </div>
        </div>
        <span className="flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
          <Sparkles className="w-3 h-3" /> Online
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 py-3 pr-1 text-xs">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-2.5 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.role === 'assistant' && (
              <div className="w-6 h-6 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0 mt-0.5">
                <Bot className="w-3.5 h-3.5" />
              </div>
            )}
            <div
              className={`p-3 rounded-xl max-w-[85%] leading-relaxed ${
                m.role === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-none'
                  : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none'
              }`}
            >
              {m.text}
            </div>
            {m.role === 'user' && (
              <div className="w-6 h-6 rounded-full bg-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-0.5">
                <User className="w-3.5 h-3.5" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-slate-400 text-xs italic">
            <Bot className="w-4 h-4 animate-bounce text-blue-400" />
            Analyzing graph topology and active entities...
          </div>
        )}
      </div>

      {/* Quick Prompts */}
      <div className="flex gap-1.5 overflow-x-auto pb-2 pt-1">
        {quickPrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(p)}
            className="text-[10px] text-slate-400 hover:text-slate-200 bg-slate-900 hover:bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-800 whitespace-nowrap transition"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-2 pt-2 border-t border-slate-800"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything about the transaction graph..."
          className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="p-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white rounded-xl transition"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
