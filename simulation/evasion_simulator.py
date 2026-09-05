import random
import time
from typing import List, Dict, Any

def generate_adversarial_evasion_stream(ring_id: int = 99, count: int = 15) -> List[Dict[str, Any]]:
    """
    Simulates a sophisticated adversary attempting to evade standard single-row and graph defenses:
    - Rotates residential IP subnets (preventing simple IP blocks)
    - Introduces random time delays/jitter (preventing high-velocity threshold triggers)
    - Slightly mutates user agent strings
    - Still linked by latent hardware canvas hash and card BIN cluster
    """
    latent_canvas_hash = f"canvas_stealth_{ring_id}_0x889a"
    stolen_bin_cluster = f"card_tok_stealth_{ring_id}"
    base_time = time.time()
    evasion_txs = []

    for i in range(count):
        user_id = f"stealth_attacker_{ring_id}_{i+1}"
        # Rotating residential IPs
        ip = f"14.139.{random.randint(10, 250)}.{random.randint(2, 250)}"
        # Randomized amounts to avoid static amount triggers
        amount = round(random.uniform(250.0, 1800.0), 2)
        # Time jitter: 5 to 15 minutes between actions
        tx_time = base_time + (i * random.uniform(300.0, 900.0))

        tx = {
            "id": f"pay_stealth_{ring_id}_{i+1:03d}",
            "user_id": user_id,
            "device_fingerprint": latent_canvas_hash,
            "ip_address": ip,
            "card_token": f"{stolen_bin_cluster}_{i%3}", # Cycles between 3 stolen cards
            "shipping_address_hash": f"stealth_addr_drop_{ring_id}",
            "merchant_id": "merchant_d2c_apparel",
            "amount": amount,
            "timestamp": tx_time,
            "status": "authorized",
            "ground_truth_label": 1,
            "attack_type": "STEALTH_EVASION_RING",
            "ring_id": f"ring_stealth_{ring_id}"
        }
        evasion_txs.append(tx)
    return evasion_txs
