import random
import time
import hashlib
from typing import List, Dict, Any

def generate_carding_attack(ring_id: int, base_time: float, count: int = 15) -> List[Dict[str, Any]]:
    """
    Simulates an automated carding / BIN testing syndicate:
    - Multiple fake user accounts
    - Shared device canvas hashes
    - Rotating stolen card tokens
    - Micro-transaction amounts (₹1 to ₹10)
    - High temporal velocity
    """
    shared_device = f"canvas_fp_{hashlib.md5(f'device_carding_{ring_id}'.encode()).hexdigest()[:12]}"
    shared_ip = f"103.21.{random.randint(10, 99)}.{random.randint(2, 250)}"
    transactions = []

    for i in range(count):
        user_id = f"bot_user_{ring_id}_{i+1}"
        card_token = f"card_bin_411122_{ring_id}_{i+1:03d}"
        amount = random.choice([1.0, 2.0, 5.0, 10.0])
        tx_time = base_time + (i * random.uniform(2.0, 8.0)) # Every few seconds

        tx = {
            "id": f"pay_carding_{ring_id}_{i+1:03d}",
            "user_id": user_id,
            "device_fingerprint": shared_device,
            "ip_address": shared_ip,
            "card_token": card_token,
            "shipping_address_hash": "digital_item_instant",
            "merchant_id": "merchant_digital_vouchers",
            "amount": amount,
            "timestamp": tx_time,
            "status": "authorized",
            "ground_truth_label": 1,
            "attack_type": "CARDING_BOTNET",
            "ring_id": f"ring_carding_{ring_id}"
        }
        transactions.append(tx)
    return transactions

def generate_promo_sybil_attack(ring_id: int, base_time: float, count: int = 12) -> List[Dict[str, Any]]:
    """
    Simulates a Promo / Referral Bonus Sybil ring:
    - Multiple burner user accounts
    - Shared physical device hardware
    - Same IP subnet (/24)
    - Fixed promo order amounts (e.g., ₹499 to claim ₹500 off)
    """
    shared_device = f"hardware_id_{hashlib.md5(f'promo_device_{ring_id}'.encode()).hexdigest()[:12]}"
    subnet_prefix = f"182.72.{random.randint(10, 90)}"
    shared_payment = f"vpa_sybil_claim_{ring_id}@okhdfcbank"
    transactions = []

    for i in range(count):
        user_id = f"sybil_usr_{ring_id}_{i+1}"
        ip_addr = f"{subnet_prefix}.{random.randint(2, 250)}"
        amount = 499.0
        tx_time = base_time + (i * random.uniform(30.0, 120.0))

        tx = {
            "id": f"pay_sybil_{ring_id}_{i+1:03d}",
            "user_id": user_id,
            "device_fingerprint": shared_device,
            "ip_address": ip_addr,
            "card_token": shared_payment,
            "shipping_address_hash": f"addr_apt_{ring_id}_unit_{i+1}",
            "merchant_id": "merchant_d2c_apparel",
            "amount": amount,
            "timestamp": tx_time,
            "status": "authorized",
            "ground_truth_label": 1,
            "attack_type": "PROMO_SYBIL_RING",
            "ring_id": f"ring_sybil_{ring_id}"
        }
        transactions.append(tx)
    return transactions

def generate_collusive_rto_attack(ring_id: int, base_time: float, count: int = 8) -> List[Dict[str, Any]]:
    """
    Simulates Collusive RTO / Return scam ring:
    - Coordinated high-value orders
    - Altered shipping addresses in same building/pincode
    - Shared underlying card / payment source
    """
    shared_card = f"card_gold_5241_{ring_id}"
    base_address = f"pincode_560034_block_{ring_id}"
    transactions = []

    for i in range(count):
        user_id = f"rto_buyer_{ring_id}_{i+1}"
        device_id = f"dev_rto_{ring_id}_{i%2}" # Shared between 2 burner phones
        ip_addr = f"49.207.{random.randint(10, 80)}.{random.randint(2, 250)}"
        amount = random.choice([4999.0, 8999.0, 12499.0])
        tx_time = base_time + (i * random.uniform(180.0, 600.0))

        tx = {
            "id": f"pay_rto_{ring_id}_{i+1:03d}",
            "user_id": user_id,
            "device_fingerprint": device_id,
            "ip_address": ip_addr,
            "card_token": shared_card,
            "shipping_address_hash": f"{base_address}_flat_{i+101}",
            "merchant_id": "merchant_electronics_hub",
            "amount": amount,
            "timestamp": tx_time,
            "status": "authorized",
            "ground_truth_label": 1,
            "attack_type": "COLLUSIVE_RTO_FRAUD",
            "ring_id": f"ring_rto_{ring_id}"
        }
        transactions.append(tx)
    return transactions
