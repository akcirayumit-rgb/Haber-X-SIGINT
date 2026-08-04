#!/usr/bin/env python3
"""Solar Activity Monitor (K-index, A-index, flares)"""
import json, sys, time, random
from datetime import datetime

FLARE_CLASSES = ["—", "A", "B", "C", "M", "X"]

try:
    print("[solar] Başlatıldı", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        print(json.dumps({
            "type": "solar",
            "k_index": random.randint(0, 9),
            "a_index": random.randint(0, 400),
            "sunspot_number": random.randint(0, 200),
            "flare_class": random.choice(FLARE_CLASSES),
            "f107_flux": round(random.uniform(65, 300), 1),
            "x_ray_flux": round(random.uniform(0.1, 1000), 2),
            "proton_flux": random.randint(0, 10000),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 5 == 0:
            print(f"[solar] {iteration} indeks ölçümü", file=sys.stderr, flush=True)
        time.sleep(1.5)
except KeyboardInterrupt:
    print("[solar] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
