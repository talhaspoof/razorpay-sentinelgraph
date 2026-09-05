import random
import time
import hashlib
from typing import List, Dict, Any
from simulation.attack_scenarios import (
    generate_carding_attack,
    generate_promo_sybil_attack,
    generate_collusive_rto_attack
)

def generate_benchmark_dataset(
    num_benign: int = 1000,
    num_carding_rings: int = 3,
    num_promo_rings: int = 3,
    num_rto_rings: int = 2
) -> List[Dict[str, Any]]:
    """
    Generates a realistic benchmark transaction dataset:
    - Benign transactions with realistic Indian e-commerce patterns (shared family devices, hostel Wi-Fi, repeat buyers)
    - Injected ground-truth coordinated fraud syndicates
    """
    random.seed(42)
    base_time = time.time() - 86400 # 24 hours ago
    dataset = []

    # 1. Generate Organic Benign Transactions
    merchants = ["merchant_fashion_d2c", "merchant_electronics_hub", "merchant_groceries", "merchant_digital_vouchers"]
    
    # 500 distinct benign users
    num_users = 500
    benign_users = [f"legit_user_{i:04d}" for i in range(num_users)]
    
    # Assign unique primary devices and cards to each user
    user_device_map = {u: f"device_fp_{u}" for u in benign_users}
    user_card_map = {u: f"card_tok_{u}" for u in benign_users}
    user_addr_map = {u: f"addr_pin_5600{random.randint(10, 99)}_{u}" for u in benign_users}
    
    # Simulate realistic 2-person family pairs sharing a home tablet (5% of users)
    for i in range(0, int(num_users * 0.05), 2):
        u1, u2 = benign_users[i], benign_users[i+1]
        shared_tablet = f"family_tablet_home_{i//2}"
        user_device_map[u1] = shared_tablet
        user_device_map[u2] = shared_tablet

    # Shared ISP / 4G IP pool
    ip_pool = [f"122.161.{random.randint(1, 254)}.{random.randint(1, 254)}" for _ in range(100)]

    for i in range(num_benign):
        user = random.choice(benign_users)
        device = user_device_map[user]
        card = user_card_map[user]
        addr = user_addr_map[user]
        ip = random.choice(ip_pool)
        merchant = random.choice(merchants)
        
        # Log-normal distribution for organic transaction amounts
        amount = round(random.lognormvariate(6.8, 0.9), 2)
        amount = max(99.0, min(amount, 45000.0))
        tx_time = base_time + random.uniform(0, 86400)

        dataset.append({
            "id": f"pay_benign_{i+1:05d}",
            "user_id": user,
            "device_fingerprint": device,
            "ip_address": ip,
            "card_token": card,
            "shipping_address_hash": addr,
            "merchant_id": merchant,
            "amount": amount,
            "timestamp": tx_time,
            "status": "authorized",
            "ground_truth_label": 0,
            "attack_type": "BENIGN",
            "ring_id": "none"
        })

    # 2. Inject Coordinated Fraud Rings
    current_time = base_time + 10000
    for r in range(num_carding_rings):
        ring_txs = generate_carding_attack(ring_id=r+1, base_time=current_time, count=15)
        dataset.extend(ring_txs)
        current_time += 15000

    for r in range(num_promo_rings):
        ring_txs = generate_promo_sybil_attack(ring_id=r+1, base_time=current_time, count=12)
        dataset.extend(ring_txs)
        current_time += 12000

    for r in range(num_rto_rings):
        ring_txs = generate_collusive_rto_attack(ring_id=r+1, base_time=current_time, count=8)
        dataset.extend(ring_txs)
        current_time += 8000

    # Sort dataset chronologically
    dataset.sort(key=lambda x: x["timestamp"])
    return dataset
