import React, { useState } from 'react';
import { Play, Flame, Gift, ShieldCheck, RefreshCw } from 'lucide-react';

export default function WebhookSimulator({ onInjectComplete }) {
  const [loading, setLoading] = useState(false);

  const injectScenario = async (type) => {
    setLoading(true);
    try {
      let payload = {};

      if (type === 'CARDING') {
        // Send a burst of 4 carding transactions in parallel
        const requests = [0, 1, 2, 3].map(i => {
          const payload = {
            event: "payment.authorized",
            payload: {
              payment: {
                entity: {
                  id: `pay_carding_${Date.now()}_${i}`,
                  amount: 200, // 200 paise = Rs 2
                  currency: "INR",
                  status: "authorized",
                  method: "card",
                  card_id: `card_bin_411122_test_${i}`,
                  notes: {
                    user_id: `bot_carder_${i+1}`,
                    device_fingerprint: "canvas_fp_demo_carding_cluster",
                    ip_address: "103.21.55.88",
                    merchant_id: "merchant_digital_vouchers"
                  }
                }
              }
            }
          };
          return fetch('/api/v1/webhooks/razorpay', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
        });
        await Promise.all(requests);
      } else if (type === 'PROMO_SYBIL') {
        // Send a burst of 4 promo abuse claims in parallel
        const requests = [0, 1, 2, 3].map(i => {
          const payload = {
            event: "payment.authorized",
            payload: {
              payment: {
                entity: {
                  id: `pay_sybil_${Date.now()}_${i}`,
                  amount: 49900, // Rs 499
                  currency: "INR",
                  status: "authorized",
                  method: "upi",
                  vpa: "sybil_claim@okhdfcbank",
                  notes: {
                    user_id: `sybil_user_${i+1}`,
                    device_fingerprint: "hardware_demo_promo_device",
                    ip_address: `182.72.44.${10+i}`,
                    merchant_id: "merchant_d2c_apparel"
                  }
                }
              }
            }
          };
          return fetch('/api/v1/webhooks/razorpay', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
        });
        await Promise.all(requests);
      } else if (type === 'BENIGN') {
        // Normal purchase
        const rnd = Math.floor(Math.random() * 10000);
        payload = {
          event: "payment.authorized",
          payload: {
            payment: {
              entity: {
                id: `pay_legit_${Date.now()}`,
                amount: Math.floor(Math.random() * 400000) + 9900,
                currency: "INR",
                status: "authorized",
                method: "upi",
                vpa: `customer_${rnd}@okaxis`,
                notes: {
                  user_id: `customer_${rnd}`,
                  device_fingerprint: `device_fp_clean_${rnd}`,
                  ip_address: `49.207.${Math.floor(Math.random()*200)}.${Math.floor(Math.random()*200)}`,
                  merchant_id: "merchant_fashion_d2c"
                }
              }
            }
          }
        };
        await fetch('/api/v1/webhooks/razorpay', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }

      onInjectComplete && onInjectComplete();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    try {
      await fetch('/api/v1/graph/reset', { method: 'POST' });
      onInjectComplete && onInjectComplete();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#111827] rounded-2xl border border-slate-800 p-5 shadow-2xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Play className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide">
            Live Razorpay Webhook Injector
          </h3>
        </div>
        <button
          onClick={handleReset}
          disabled={loading}
          className="text-xs text-slate-400 hover:text-white flex items-center gap-1 bg-slate-900 hover:bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-800 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Reset Graph
        </button>
      </div>

      <p className="text-xs text-slate-400 mt-2 mb-3">
        Simulate live incoming Razorpay webhooks to observe real-time graph linking, anomaly scoring, and AI forensic response:
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
        <button
          onClick={() => injectScenario('CARDING')}
          disabled={loading}
          className="flex items-center justify-center gap-2 p-3 bg-red-950/40 hover:bg-red-900/60 border border-red-800/60 text-red-300 rounded-xl font-semibold text-xs transition shadow-md shadow-red-950/30"
        >
          <Flame className="w-4 h-4 text-red-400" />
          <span>Inject Carding Ring (₹2)</span>
        </button>

        <button
          onClick={() => injectScenario('PROMO_SYBIL')}
          disabled={loading}
          className="flex items-center justify-center gap-2 p-3 bg-purple-950/40 hover:bg-purple-900/60 border border-purple-800/60 text-purple-300 rounded-xl font-semibold text-xs transition shadow-md shadow-purple-950/30"
        >
          <Gift className="w-4 h-4 text-purple-400" />
          <span>Inject Promo Sybil (₹499)</span>
        </button>

        <button
          onClick={() => injectScenario('BENIGN')}
          disabled={loading}
          className="flex items-center justify-center gap-2 p-3 bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-800/60 text-emerald-300 rounded-xl font-semibold text-xs transition shadow-md shadow-emerald-950/30"
        >
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Inject Legit Purchase</span>
        </button>
      </div>
    </div>
  );
}
