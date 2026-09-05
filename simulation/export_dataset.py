import sys
import os
import json
import pandas as pd

# Add root and backend to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "backend"))

from simulation.generator import generate_benchmark_dataset
from simulation.evasion_simulator import generate_adversarial_evasion_stream

def export_all_data():
    print("[*] Generating full benchmark dataset...")
    # 1. Generate benign + 3 fraud topologies
    dataset = generate_benchmark_dataset(
        num_benign=1000,
        num_carding_rings=3,
        num_promo_rings=3,
        num_rto_rings=2
    )
    
    # 2. Add adversarial evasion stream
    evasion_txs = generate_adversarial_evasion_stream(ring_id=99, count=15)
    dataset.extend(evasion_txs)
    dataset.sort(key=lambda x: x["timestamp"])

    data_dir = os.path.join(ROOT_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)

    # 3. Export to CSV
    csv_path = os.path.join(data_dir, "benchmark_dataset.csv")
    df = pd.DataFrame(dataset)
    df.to_csv(csv_path, index=False)
    print(f"[OK] Exported {len(dataset)} transactions to CSV: {csv_path}")

    # 4. Export to JSON
    json_path = os.path.join(data_dir, "benchmark_dataset.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
    print(f"[OK] Exported {len(dataset)} transactions to JSON: {json_path}")

    # Print summary statistics
    print("\n" + "=" * 60)
    print("  DATASET BREAKDOWN SUMMARY")
    print("=" * 60)
    print(df["attack_type"].value_counts())
    print("=" * 60)

if __name__ == "__main__":
    export_all_data()
